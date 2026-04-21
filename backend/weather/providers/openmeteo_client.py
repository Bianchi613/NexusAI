"""Fallback de previsao via Open-Meteo sem necessidade de API key."""

from __future__ import annotations

from datetime import datetime, timezone

import requests

from backend.config.settings import settings


OPEN_METEO_WEATHER_CODES = {
    0: "Ceu limpo",
    1: "Predominio de sol",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Nevoeiro",
    48: "Nevoeiro com geada",
    51: "Garoa fraca",
    53: "Garoa moderada",
    55: "Garoa intensa",
    56: "Garoa congelante fraca",
    57: "Garoa congelante intensa",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva intensa",
    66: "Chuva congelante fraca",
    67: "Chuva congelante intensa",
    71: "Neve fraca",
    73: "Neve moderada",
    75: "Neve intensa",
    77: "Graos de neve",
    80: "Pancadas de chuva fracas",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva fortes",
    85: "Pancadas de neve fracas",
    86: "Pancadas de neve fortes",
    95: "Trovoadas",
    96: "Trovoadas com granizo fraco",
    99: "Trovoadas com granizo forte",
}

KNOWN_BRAZILIAN_CAPITAL_COORDS = {
    ("brasilia", "DF"): (-15.793889, -47.882778),
    ("sao paulo", "SP"): (-23.55052, -46.633308),
    ("rio de janeiro", "RJ"): (-22.906847, -43.172897),
    ("belo horizonte", "MG"): (-19.916681, -43.934493),
    ("salvador", "BA"): (-12.977749, -38.50163),
    ("curitiba", "PR"): (-25.428954, -49.267137),
    ("porto alegre", "RS"): (-30.034647, -51.217658),
    ("recife", "PE"): (-8.047562, -34.876964),
    ("manaus", "AM"): (-3.119028, -60.021731),
    ("belem", "PA"): (-1.455754, -48.490179),
}


class OpenMeteoClient:
    """Consulta previsao diaria via Open-Meteo."""

    def __init__(self) -> None:
        self.forecast_url = settings.weather_openmeteo_forecast_url
        self.geocoding_url = settings.weather_openmeteo_geocoding_url
        self.timeout = settings.weather_request_timeout_seconds

    @property
    def is_enabled(self) -> bool:
        """API publica, sem chave, disponivel por padrao."""
        return True

    def fetch_weekly_forecast(self, *, city: str, state_code: str) -> dict:
        """Retorna previsao de 7 dias com maxima, minima e probabilidade de chuva."""
        latitude, longitude = self._resolve_coordinates(city=city, state_code=state_code)
        response = requests.get(
            self.forecast_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "forecast_days": 7,
                "timezone": "America/Sao_Paulo",
            },
            timeout=self.timeout,
            headers={"User-Agent": "NexusAI/1.0"},
        )
        response.raise_for_status()
        payload = response.json()

        daily_payload = payload.get("daily", {})
        dates = daily_payload.get("time", [])
        weather_codes = daily_payload.get("weather_code", [])
        max_temps = daily_payload.get("temperature_2m_max", [])
        min_temps = daily_payload.get("temperature_2m_min", [])
        rain_probabilities = daily_payload.get("precipitation_probability_max", [])

        daily = []
        for index, date_value in enumerate(dates[:7]):
            weather_code = weather_codes[index] if index < len(weather_codes) else None
            max_temp = max_temps[index] if index < len(max_temps) else None
            min_temp = min_temps[index] if index < len(min_temps) else None
            rain_probability = rain_probabilities[index] if index < len(rain_probabilities) else None

            daily.append(
                {
                    "date": date_value,
                    "condition_code": str(weather_code) if weather_code is not None else None,
                    "condition": OPEN_METEO_WEATHER_CODES.get(weather_code, "Condicao indisponivel"),
                    "min_temp_c": round(min_temp) if min_temp is not None else None,
                    "max_temp_c": round(max_temp) if max_temp is not None else None,
                    "uv_index": None,
                    "rain_probability": round(rain_probability) if rain_probability is not None else None,
                }
            )

        return {
            "city": city,
            "state_code": state_code,
            "source_name": "Open-Meteo",
            "source_url": self.forecast_url,
            "updated_at": datetime.now(timezone.utc),
            "daily": daily,
            "extra_payload": {
                "latitude": latitude,
                "longitude": longitude,
                "timezone": payload.get("timezone"),
            },
        }

    def _resolve_coordinates(self, *, city: str, state_code: str) -> tuple[float, float]:
        normalized_city = city.strip().lower()
        known_coordinates = KNOWN_BRAZILIAN_CAPITAL_COORDS.get((normalized_city, state_code.upper()))
        if known_coordinates is not None:
            return known_coordinates

        response = requests.get(
            self.geocoding_url,
            params={
                "name": city,
                "count": 10,
                "language": "pt",
                "countryCode": "BR",
                "format": "json",
            },
            timeout=self.timeout,
            headers={"User-Agent": "NexusAI/1.0"},
        )
        response.raise_for_status()
        payload = response.json()

        for item in payload.get("results", []):
            admin1 = str(item.get("admin1") or "").strip().lower()
            result_state_code = str(item.get("country_code") or "").upper()
            if result_state_code != "BR":
                continue
            if admin1 and state_code.strip().lower() in admin1:
                return float(item["latitude"]), float(item["longitude"])

        first_result = next(iter(payload.get("results", []) or []), None)
        if first_result is None:
            raise ValueError(f"Coordenadas nao encontradas para {city}/{state_code}")
        return float(first_result["latitude"]), float(first_result["longitude"])
