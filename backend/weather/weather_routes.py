"""Rotas publicas do modulo de clima."""

from fastapi import APIRouter, Query

from backend.weather.weather_controller import get_weather_overview_controller, list_weather_alerts_controller
from backend.weather.weather_schema import WeatherAlertResponse, WeatherOverviewResponse


router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/overview", response_model=WeatherOverviewResponse)
def weather_overview_route() -> WeatherOverviewResponse:
    """Retorna previsao consolidada e alertas para a aba de clima."""
    return get_weather_overview_controller()


@router.get("/alerts", response_model=list[WeatherAlertResponse])
def weather_alerts_route(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[WeatherAlertResponse]:
    """Lista alertas ativos da camada meteorologica."""
    return list_weather_alerts_controller(limit=limit)
