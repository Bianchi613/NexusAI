"""Cliente para previsao por municipio via CPTEC/INPE XML."""

from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import unicodedata
import xml.etree.ElementTree as ET

import requests

from backend.config.settings import settings


CPTEC_CONDITION_LABELS = {
    "ec": "Encoberto com chuvas isoladas",
    "ci": "Chuvas isoladas",
    "c": "Chuva",
    "in": "Instavel",
    "pp": "Possibilidade de pancadas de chuva",
    "cm": "Chuva pela manha",
    "cn": "Chuva a noite",
    "pt": "Pancadas de chuva a tarde",
    "pm": "Pancadas de chuva pela manha",
    "np": "Nublado com pancadas de chuva",
    "pc": "Pancadas de chuva",
    "pn": "Parcialmente nublado",
    "cv": "Chuvisco",
    "ch": "Chuvoso",
    "t": "Tempestade",
    "ps": "Predominio de sol",
    "e": "Encoberto",
    "n": "Nublado",
    "cl": "Ceu claro",
    "nv": "Nevoeiro",
    "g": "Geada",
    "ne": "Neve",
    "nd": "Nao definido",
    "pnt": "Pancadas de chuva a noite",
    "psc": "Possibilidade de chuva",
    "pcm": "Possibilidade de chuva pela manha",
    "pct": "Possibilidade de chuva a tarde",
    "pcn": "Possibilidade de chuva a noite",
    "npt": "Nublado com pancadas a tarde",
    "npn": "Nublado com pancadas a noite",
    "ncn": "Nublado com possibilidade de chuva a noite",
    "nct": "Nublado com possibilidade de chuva a tarde",
    "ncm": "Nublado com possibilidade de chuva pela manha",
    "npm": "Nublado com pancadas pela manha",
    "npp": "Nublado com possibilidade de chuva",
    "vn": "Variacao de nebulosidade",
    "ct": "Chuva a tarde",
    "ppn": "Possibilidade de pancadas de chuva a noite",
    "ppt": "Possibilidade de pancadas de chuva a tarde",
    "ppm": "Possibilidade de pancadas de chuva pela manha",
}


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value or "")
    return "".join(character for character in normalized if not unicodedata.combining(character))


class CPTECClient:
    """Consulta municipios e previsoes do CPTEC/INPE."""

    def __init__(self) -> None:
        self.base_url = settings.weather_cptec_base_url.rstrip("/")
        self.timeout = max(1, settings.weather_cptec_timeout_seconds)

    def fetch_weekly_forecast(self, *, city: str, state_code: str) -> dict:
        """Retorna previsao semanal normalizada para uma cidade."""
        city_id = self._find_city_id(city=city, state_code=state_code)
        response = requests.get(
            f"{self.base_url}/cidade/7dias/{city_id}/previsao.xml",
            timeout=self.timeout,
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)
        updated_at = self._parse_cptec_date(self._read_text(root, "atualizacao"))
        normalized_city = self._read_text(root, "nome") or city
        normalized_state_code = (self._read_text(root, "uf") or state_code).upper()
        daily = []

        for node in root.findall("previsao"):
            condition_code = (self._read_text(node, "tempo") or "").strip().lower() or None
            daily.append(
                {
                    "date": self._read_text(node, "dia"),
                    "condition_code": condition_code,
                    "condition": CPTEC_CONDITION_LABELS.get(condition_code or "", "Condicao indisponivel"),
                    "min_temp_c": self._read_int(node, "minima"),
                    "max_temp_c": self._read_int(node, "maxima"),
                    "uv_index": self._read_float(node, "iuv"),
                    "rain_probability": None,
                }
            )

        return {
            "city": normalized_city,
            "state_code": normalized_state_code,
            "source_name": "CPTEC/INPE",
            "source_url": f"{self.base_url}/cidade/7dias/{city_id}/previsao.xml",
            "updated_at": updated_at or datetime.now(timezone.utc),
            "daily": [item for item in daily if item.get("date")],
            "extra_payload": {"cptec_city_id": city_id},
        }

    def _find_city_id(self, *, city: str, state_code: str) -> str:
        search_value = _strip_accents(city).lower()
        response = requests.get(
            f"{self.base_url}/listaCidades",
            params={"city": search_value},
            timeout=self.timeout,
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)
        normalized_target_city = _strip_accents(city).lower()
        normalized_target_state = state_code.strip().upper()

        exact_candidates: list[tuple[str, str]] = []
        fuzzy_candidates: list[tuple[str, str]] = []

        for city_node in root.findall("cidade"):
            found_city = self._read_text(city_node, "nome") or ""
            found_state = (self._read_text(city_node, "uf") or "").upper()
            found_id = self._read_text(city_node, "id") or ""
            normalized_found_city = _strip_accents(found_city).lower()

            if found_state != normalized_target_state or not found_id:
                continue

            if normalized_found_city == normalized_target_city:
                exact_candidates.append((found_city, found_id))
                continue

            if normalized_found_city.startswith(normalized_target_city):
                fuzzy_candidates.append((found_city, found_id))

        candidates = exact_candidates or fuzzy_candidates
        if not candidates:
            raise ValueError(f"Cidade nao encontrada no CPTEC: {city}/{state_code}")
        return candidates[0][1]

    @staticmethod
    def _read_text(node: ET.Element, tag_name: str) -> str | None:
        child = node.find(tag_name)
        if child is None or child.text is None:
            return None
        value = unescape(child.text).strip()
        return value or None

    @staticmethod
    def _read_int(node: ET.Element, tag_name: str) -> int | None:
        value = CPTECClient._read_text(node, tag_name)
        if value is None:
            return None
        try:
            return int(float(value))
        except ValueError:
            return None

    @staticmethod
    def _read_float(node: ET.Element, tag_name: str) -> float | None:
        value = CPTECClient._read_text(node, tag_name)
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_cptec_date(value: str | None) -> datetime | None:
        if not value:
            return None
        for pattern in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(value, pattern).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return None
