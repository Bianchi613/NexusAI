"""Cliente para leitura de alertas em RSS do INMET."""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha1
from html import unescape
import re
import xml.etree.ElementTree as ET

import requests

from backend.config.settings import settings


HTML_TAG_RE = re.compile(r"<[^>]+>")
MULTISPACE_RE = re.compile(r"\s+")


class INMETAlertClient:
    """Consulta o feed RSS de avisos meteorologicos do INMET."""

    def __init__(self) -> None:
        self.feed_url = settings.weather_inmet_alerts_url
        self.timeout = settings.weather_request_timeout_seconds

    def fetch_alerts(self) -> list[dict]:
        """Retorna alertas ativos normalizados a partir do RSS."""
        response = requests.get(self.feed_url, timeout=self.timeout, headers={"User-Agent": "NexusAI/1.0"})
        response.raise_for_status()

        root = ET.fromstring(response.content)
        items = root.findall("./channel/item")
        if not items:
            items = root.findall(".//item")

        alerts = []
        collected_at = datetime.now(timezone.utc)
        for item in items:
            title = self._read_text(item, "title")
            if not title:
                continue

            description_html = self._read_text(item, "description") or ""
            summary = self._strip_html(description_html)
            link = self._read_text(item, "link")
            published_at = self._parse_rss_date(self._read_text(item, "pubDate"))
            effective_at = self._extract_datetime(summary, "inicio")
            expires_at = self._extract_datetime(summary, "fim")
            areas = self._extract_areas(summary)
            severity = self._infer_severity(" ".join(filter(None, [title, summary])))
            status = "ativo"
            external_id = self._build_external_id(title=title, link=link, published_at=published_at, summary=summary)

            alerts.append(
                {
                    "external_id": external_id,
                    "title": title,
                    "summary": summary or None,
                    "severity": severity,
                    "status": status,
                    "area": areas[0] if areas else None,
                    "areas": areas,
                    "source_url": link,
                    "published_at": published_at,
                    "effective_at": effective_at,
                    "expires_at": expires_at,
                    "is_active": True,
                    "payload": {
                        "title": title,
                        "description": summary,
                    },
                    "collected_at": collected_at,
                }
            )

        return alerts

    @staticmethod
    def _build_external_id(*, title: str, link: str | None, published_at: datetime | None, summary: str) -> str:
        base_value = "|".join(
            [
                title.strip().lower(),
                (link or "").strip().lower(),
                published_at.isoformat() if published_at is not None else "",
                summary[:120].strip().lower(),
            ]
        )
        return sha1(base_value.encode("utf-8")).hexdigest()

    @staticmethod
    def _strip_html(value: str) -> str:
        without_tags = HTML_TAG_RE.sub(" ", unescape(value or ""))
        return MULTISPACE_RE.sub(" ", without_tags).strip()

    @staticmethod
    def _infer_severity(value: str) -> str:
        lowered = value.lower()
        if "grande perigo" in lowered:
            return "grande-perigo"
        if "perigo potencial" in lowered:
            return "perigo-potencial"
        if "perigo" in lowered:
            return "perigo"
        if any(term in lowered for term in ("tempestade", "vendaval", "chuva intensa", "granizo")):
            return "atencao"
        return "informativo"

    @staticmethod
    def _extract_areas(summary: str) -> list[str]:
        patterns = (
            r"(?:aviso para as areas|aviso para as áreas)\s*:\s*([^.;]+)",
            r"(?:areas afetadas|area afetada)\s*:\s*([^.;]+)",
            r"(?:abrange|atinge)\s+([^.;]+)",
        )
        for pattern in patterns:
            match = re.search(pattern, summary, flags=re.IGNORECASE)
            if match is None:
                continue
            raw_value = match.group(1)
            parts = [part.strip(" ,-") for part in re.split(r",|/| e ", raw_value) if part.strip(" ,-")]
            if parts:
                return parts
        return []

    @staticmethod
    def _extract_datetime(summary: str, label: str) -> datetime | None:
        patterns = (
            rf"{label}\s*:\s*(\d{{2}}/\d{{2}}/\d{{4}}\s+\d{{2}}:\d{{2}})",
            rf"{label}\s*:\s*(\d{{2}}-\d{{2}}-\d{{4}}\s+\d{{2}}:\d{{2}})",
        )
        for pattern in patterns:
            match = re.search(pattern, summary, flags=re.IGNORECASE)
            if match is None:
                continue
            value = match.group(1)
            for date_pattern in ("%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M"):
                try:
                    return datetime.strptime(value, date_pattern).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _parse_rss_date(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _read_text(node: ET.Element, tag_name: str) -> str | None:
        child = node.find(tag_name)
        if child is None or child.text is None:
            return None
        value = child.text.strip()
        return value or None
