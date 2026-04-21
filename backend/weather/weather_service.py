"""Servico principal do modulo de clima."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from Engine.app.core.article_filters import slugify
from backend.config.settings import settings
from backend.weather.providers.cptec_client import CPTECClient
from backend.weather.providers.inmet_client import INMETAlertClient
from backend.weather.providers.openmeteo_client import OpenMeteoClient
from backend.weather.providers.openweather_client import OpenWeatherClient
from backend.weather.weather_repository import WeatherRepository
from backend.weather.weather_schema import (
    WeatherAlertResponse,
    WeatherBrazilSummaryResponse,
    WeatherForecastDayResponse,
    WeatherLocationForecastResponse,
    WeatherOverviewResponse,
)


SEVERE_ALERT_LEVELS = {"grande-perigo", "perigo", "perigo-potencial"}

weather_repository = WeatherRepository()
cptec_client = CPTECClient()
inmet_client = INMETAlertClient()
openmeteo_client = OpenMeteoClient()
openweather_client = OpenWeatherClient()


class ForecastProviderUnavailable(Exception):
    """Sinaliza que a fonte externa de previsao esta temporariamente indisponivel."""


def get_weather_overview() -> WeatherOverviewResponse:
    """Retorna o pacote principal usado pela aba de clima."""
    monitored_locations = _get_monitored_locations()
    forecasts: list[WeatherLocationForecastResponse] = []
    remote_fetch_enabled = True

    for location in monitored_locations:
        try:
            forecast = _get_location_forecast(location, allow_remote_fetch=remote_fetch_enabled)
        except ForecastProviderUnavailable:
            remote_fetch_enabled = False
            forecast = None

        if forecast is not None:
            forecasts.append(forecast)

    locations = [forecast for forecast in forecasts if forecast is not None]
    alerts = list_weather_alerts(limit=8)
    summary = _build_brazil_summary(locations=locations, alerts=alerts)
    return WeatherOverviewResponse(summary=summary, locations=locations, alerts=alerts)


def list_weather_alerts(*, limit: int = 20) -> list[WeatherAlertResponse]:
    """Lista alertas ativos com refresh opportunistico."""
    cached_alerts = weather_repository.list_active_alerts(limit=limit)
    now = datetime.now(timezone.utc)

    is_cache_stale = (
        not cached_alerts
        or any(
            _is_stale(
                reference_datetime=alert.collected_at,
                ttl_minutes=settings.weather_alert_ttl_minutes,
                now=now,
            )
            for alert in cached_alerts[:1]
        )
    )

    if is_cache_stale:
        try:
            fresh_alerts = inmet_client.fetch_alerts()
            weather_repository.upsert_alerts(source_name="INMET", alerts=fresh_alerts)
            cached_alerts = weather_repository.list_active_alerts(limit=limit)
        except Exception:
            # Mantemos os ultimos dados validos quando a fonte externa falhar.
            pass

    return [
        WeatherAlertResponse(
            external_id=alert.external_id,
            source_name=alert.source_name,
            title=alert.title,
            summary=alert.summary,
            severity=alert.severity,
            status=alert.status,
            area=alert.area,
            areas=list(alert.areas or []),
            source_url=alert.source_url,
            published_at=_normalize_datetime(alert.published_at),
            effective_at=_normalize_datetime(alert.effective_at),
            expires_at=_normalize_datetime(alert.expires_at),
            is_active=alert.is_active,
        )
        for alert in cached_alerts[:limit]
    ]


def _get_location_forecast(
    location: dict[str, str],
    *,
    allow_remote_fetch: bool,
) -> WeatherLocationForecastResponse | None:
    """Retorna a previsao da localidade, usando cache quando apropriado."""
    location_key = location["location_key"]
    snapshot = weather_repository.get_forecast_by_location_key(location_key)
    now = datetime.now(timezone.utc)

    snapshot_expires_at = _normalize_datetime(snapshot.expires_at) if snapshot is not None else None
    if snapshot is not None and snapshot_expires_at is not None and snapshot_expires_at > now:
        return _map_location_snapshot(snapshot)

    if not allow_remote_fetch:
        if snapshot is None:
            return None
        return _map_location_snapshot(snapshot)

    try:
        forecast_payload = _fetch_forecast_from_sources(city=location["city"], state_code=location["state_code"])
        headline, summary, advisory_items = _build_location_editorial_copy(
            city=forecast_payload["city"],
            state_code=forecast_payload["state_code"],
            daily=forecast_payload["daily"],
        )

        weather_repository.upsert_forecast(
            location_key=location_key,
            city_name=forecast_payload["city"],
            state_code=forecast_payload["state_code"],
            state_name=location.get("state_name"),
            source_name=forecast_payload["source_name"],
            source_url=forecast_payload.get("source_url"),
            headline=headline,
            summary=summary,
            daily_forecast=forecast_payload["daily"],
            advisory_items=advisory_items,
            extra_payload=dict(forecast_payload.get("extra_payload") or {}),
            collected_at=forecast_payload["updated_at"],
            expires_at=now + timedelta(minutes=settings.weather_forecast_ttl_minutes),
        )
        snapshot = weather_repository.get_forecast_by_location_key(location_key)
    except ForecastProviderUnavailable:
        if snapshot is not None:
            return _map_location_snapshot(snapshot)
        raise
    except Exception:
        if snapshot is None:
            return None

    return _map_location_snapshot(snapshot)


def _fetch_forecast_from_sources(*, city: str, state_code: str) -> dict[str, Any]:
    """Consulta a principal fonte brasileira e usa fallback quando necessario."""
    try:
        return cptec_client.fetch_weekly_forecast(city=city, state_code=state_code)
    except Exception:
        if openmeteo_client.is_enabled:
            try:
                return openmeteo_client.fetch_weekly_forecast(city=city, state_code=state_code)
            except Exception:
                pass
        if openweather_client.is_enabled:
            return openweather_client.fetch_weekly_forecast(city=city, state_code=state_code)
        raise ForecastProviderUnavailable()


def _map_location_snapshot(snapshot) -> WeatherLocationForecastResponse:
    """Converte o snapshot persistido para o schema publico."""
    return WeatherLocationForecastResponse(
        location_key=snapshot.location_key,
        city=snapshot.city_name,
        state_code=snapshot.state_code,
        state_name=snapshot.state_name,
        display_name=f"{snapshot.city_name}, {snapshot.state_code}",
        headline=snapshot.headline or f"Panorama da semana em {snapshot.city_name}",
        summary=snapshot.summary or "Previsao da semana indisponivel no momento.",
        advisory_items=list(snapshot.advisory_items or []),
        source_name=snapshot.source_name,
        source_url=snapshot.source_url,
        updated_at=_normalize_datetime(snapshot.collected_at),
        daily=[
            WeatherForecastDayResponse(
                date=str(item.get("date")),
                condition_code=item.get("condition_code"),
                condition=str(item.get("condition") or "Condicao indisponivel"),
                min_temp_c=_coerce_int(item.get("min_temp_c")),
                max_temp_c=_coerce_int(item.get("max_temp_c")),
                uv_index=_coerce_float(item.get("uv_index")),
                rain_probability=_coerce_int(item.get("rain_probability")),
            )
            for item in list(snapshot.daily_forecast or [])
            if item.get("date")
        ],
    )


def _build_location_editorial_copy(*, city: str, state_code: str, daily: list[dict]) -> tuple[str, str, list[str]]:
    """Transforma a previsao bruta em texto util para a interface."""
    if not daily:
        return (
            f"Semana sem previsao consolidada para {city}",
            f"Nao foi possivel montar o resumo da semana para {city}, {state_code}.",
            [],
        )

    first_day = daily[0]
    min_values = [item.get("min_temp_c") for item in daily if item.get("min_temp_c") is not None]
    max_values = [item.get("max_temp_c") for item in daily if item.get("max_temp_c") is not None]
    range_text = _build_temperature_range(min_values=min_values, max_values=max_values)
    rainy_days = sum(1 for item in daily if _is_rain_condition(str(item.get("condition") or "")))
    hot_days = sum(1 for item in daily if (item.get("max_temp_c") or -999) >= 32)
    cold_days = sum(1 for item in daily if (item.get("min_temp_c") or 999) <= 12)

    headline = f"{city} abre a semana com {str(first_day.get('condition') or 'tempo variavel').lower()}."
    summary = (
        f"Previsao para {city}, {state_code}, com {range_text.lower()} ao longo dos proximos dias. "
        f"A fonte principal usada foi {daily_source_name(daily)}."
    )

    advisory_items: list[str] = []
    if rainy_days >= 3:
        advisory_items.append("Sequencia de dias com chuva ou instabilidade na grade da semana.")
    if hot_days >= 2:
        advisory_items.append("Calor persistente em parte da semana, com maximas acima de 32C.")
    if cold_days >= 2:
        advisory_items.append("Madrugadas mais frias aparecem em pelo menos dois dias monitorados.")
    if not advisory_items:
        advisory_items.append("Tendencia de semana mais estavel, com leitura util para planejamento diario.")

    return headline, summary, advisory_items[:3]


def _build_brazil_summary(
    *,
    locations: list[WeatherLocationForecastResponse],
    alerts: list[WeatherAlertResponse],
) -> WeatherBrazilSummaryResponse:
    """Monta o resumo nacional da aba de clima."""
    min_values = [day.min_temp_c for location in locations for day in location.daily if day.min_temp_c is not None]
    max_values = [day.max_temp_c for location in locations for day in location.daily if day.max_temp_c is not None]
    severe_alert_count = sum(1 for alert in alerts if alert.severity in SEVERE_ALERT_LEVELS)
    source_names = sorted({location.source_name for location in locations} | {alert.source_name for alert in alerts})
    updated_candidates = [_normalize_datetime(location.updated_at) for location in locations if location.updated_at is not None]
    updated_candidates.extend(_normalize_datetime(alert.published_at) for alert in alerts if alert.published_at is not None)
    updated_at = max(updated_candidates) if updated_candidates else None

    range_text = _build_temperature_range(min_values=min_values, max_values=max_values)
    headline = "Panorama da semana no Brasil com foco em capitais de referencia."
    if severe_alert_count > 0:
        headline = f"Brasil entra na semana com {severe_alert_count} alerta(s) de maior severidade em acompanhamento."

    summary = (
        f"O monitoramento cruza previsoes por capitais que representam estados-chave do pais. "
        f"A faixa observada vai de {range_text.lower()}."
    )
    if alerts:
        summary += f" Ha {len(alerts)} alerta(s) ativos do INMET no painel."
    else:
        summary += " Nao ha alertas ativos no painel neste momento."

    advisory_items = []
    if severe_alert_count > 0:
        advisory_items.append("Ha alertas relevantes do INMET na grade superior da pagina.")
    if len(alerts) > severe_alert_count and alerts:
        advisory_items.append("Avisos de menor severidade continuam visiveis para acompanhamento rapido.")
    if locations:
        advisory_items.append("A leitura por estado usa a capital como ponto de referencia operacional.")

    return WeatherBrazilSummaryResponse(
        headline=headline,
        summary=summary,
        advisory_items=advisory_items[:3],
        source_names=source_names,
        updated_at=updated_at,
        location_count=len(locations),
        active_alert_count=len(alerts),
        severe_alert_count=severe_alert_count,
    )


def _build_temperature_range(*, min_values: list[int | None], max_values: list[int | None]) -> str:
    """Formata a faixa termica resumida."""
    normalized_mins = [value for value in min_values if value is not None]
    normalized_maxs = [value for value in max_values if value is not None]
    if not normalized_mins and not normalized_maxs:
        return "temperaturas indisponiveis"
    if not normalized_mins:
        return f"maximas de ate {max(normalized_maxs)}C"
    if not normalized_maxs:
        return f"minimas a partir de {min(normalized_mins)}C"
    return f"minimas de {min(normalized_mins)}C e maximas de {max(normalized_maxs)}C"


def _is_rain_condition(condition: str) -> bool:
    lowered = condition.lower()
    return any(term in lowered for term in ("chuva", "tempestade", "instavel", "chuvisco"))


def daily_source_name(daily: list[dict]) -> str:
    """Mantem a copy simples quando a origem ja foi resolvida na camada superior."""
    return "uma fonte meteorologica configurada"


def _get_monitored_locations() -> list[dict[str, str]]:
    """Le e normaliza a lista de capitais usadas na aba de clima."""
    locations: list[dict[str, str]] = []

    for raw_item in settings.weather_default_locations.split(";"):
        item = raw_item.strip()
        if not item:
            continue
        parts = [part.strip() for part in item.split("|")]
        if len(parts) < 2:
            continue

        city = parts[0]
        state_code = parts[1].upper()
        state_name = parts[2] if len(parts) > 2 and parts[2] else None
        locations.append(
            {
                "location_key": slugify(f"{city}-{state_code}"),
                "city": city,
                "state_code": state_code,
                "state_name": state_name,
            }
        )

    return locations


def _is_stale(*, reference_datetime: datetime | None, ttl_minutes: int, now: datetime) -> bool:
    """Indica se um registro passou da janela de cache."""
    if reference_datetime is None:
        return True
    normalized_reference = _normalize_datetime(reference_datetime)
    if normalized_reference is None:
        return True
    return normalized_reference + timedelta(minutes=ttl_minutes) <= now


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_datetime(value: datetime | None) -> datetime | None:
    """Converte datas sem timezone para UTC antes de comparar ou serializar."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
