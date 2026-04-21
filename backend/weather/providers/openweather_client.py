"""Cliente opcional para fallback de previsao via OpenWeather."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

import requests

from backend.config.settings import settings


class OpenWeatherClient:
    """Usa a API forecast5 como fallback quando o CPTEC nao responder."""

    def __init__(self) -> None:
        self.api_key = settings.weather_openweather_api_key
        self.forecast_url = settings.weather_openweather_forecast_url
        self.timeout = settings.weather_request_timeout_seconds

    @property
    def is_enabled(self) -> bool:
        """Indica se o fallback esta configurado."""
        return bool(self.api_key)

    def fetch_weekly_forecast(self, *, city: str, state_code: str) -> dict:
        """Agrega os blocos de 3h em uma previsao diaria simplificada."""
        if not self.is_enabled:
            raise ValueError("OpenWeather fallback nao configurado.")

        response = requests.get(
            self.forecast_url,
            params={
                "q": f"{city},{state_code},BR",
                "appid": self.api_key,
                "units": "metric",
                "lang": "pt_br",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()

        days: dict[str, list[dict]] = defaultdict(list)
        for item in payload.get("list", []):
            timestamp = item.get("dt")
            if timestamp is None:
                continue
            date_key = datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat()
            days[date_key].append(item)

        aggregated_days = []
        for date_key, items in sorted(days.items())[:5]:
            temps_min = [entry.get("main", {}).get("temp_min") for entry in items if entry.get("main")]
            temps_max = [entry.get("main", {}).get("temp_max") for entry in items if entry.get("main")]
            pops = [entry.get("pop") for entry in items if entry.get("pop") is not None]
            weather_items = [entry.get("weather", [{}])[0] for entry in items if entry.get("weather")]
            primary_weather = weather_items[0] if weather_items else {}

            aggregated_days.append(
                {
                    "date": date_key,
                    "condition_code": primary_weather.get("icon"),
                    "condition": str(primary_weather.get("description") or "Condicao indisponivel").capitalize(),
                    "min_temp_c": round(min(temps_min)) if temps_min else None,
                    "max_temp_c": round(max(temps_max)) if temps_max else None,
                    "uv_index": None,
                    "rain_probability": round(max(pops) * 100) if pops else None,
                }
            )

        city_payload = payload.get("city", {})
        return {
            "city": city_payload.get("name") or city,
            "state_code": state_code,
            "source_name": "OpenWeather",
            "source_url": self.forecast_url,
            "updated_at": datetime.now(timezone.utc),
            "daily": aggregated_days,
            "extra_payload": {
                "timezone": city_payload.get("timezone"),
                "coord": city_payload.get("coord"),
            },
        }
