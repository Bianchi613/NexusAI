"""Controller HTTP do modulo de clima."""

from backend.weather.weather_schema import WeatherAlertResponse, WeatherOverviewResponse
from backend.weather.weather_service import get_weather_overview, list_weather_alerts


def get_weather_overview_controller() -> WeatherOverviewResponse:
    """Retorna o pacote principal da aba de clima."""
    return get_weather_overview()


def list_weather_alerts_controller(*, limit: int) -> list[WeatherAlertResponse]:
    """Lista alertas ativos do painel de clima."""
    return list_weather_alerts(limit=limit)
