"""Schemas publicos do modulo de clima."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class WeatherForecastDayResponse(BaseModel):
    """Representa um dia da previsao normalizada."""

    date: str
    condition_code: str | None = None
    condition: str
    min_temp_c: int | None = None
    max_temp_c: int | None = None
    uv_index: float | None = None
    rain_probability: int | None = None


class WeatherLocationForecastResponse(BaseModel):
    """Forecast consolidado de uma localidade monitorada."""

    location_key: str
    city: str
    state_code: str
    state_name: str | None = None
    display_name: str
    headline: str
    summary: str
    advisory_items: list[str]
    source_name: str
    source_url: str | None = None
    updated_at: datetime | None = None
    daily: list[WeatherForecastDayResponse]


class WeatherAlertResponse(BaseModel):
    """Alerta meteorologico disponivel ao frontend."""

    external_id: str
    source_name: str
    title: str
    summary: str | None = None
    severity: str
    status: str
    area: str | None = None
    areas: list[str]
    source_url: str | None = None
    published_at: datetime | None = None
    effective_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool


class WeatherBrazilSummaryResponse(BaseModel):
    """Resumo da leitura nacional da semana."""

    headline: str
    summary: str
    advisory_items: list[str]
    source_names: list[str]
    updated_at: datetime | None = None
    location_count: int
    active_alert_count: int
    severe_alert_count: int


class WeatherOverviewResponse(BaseModel):
    """Pacote principal consumido pela aba de clima."""

    summary: WeatherBrazilSummaryResponse
    locations: list[WeatherLocationForecastResponse]
    alerts: list[WeatherAlertResponse]
