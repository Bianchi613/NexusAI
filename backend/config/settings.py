"""Configuracoes basicas da API do portal."""

import os
from dataclasses import dataclass


DEFAULT_WEATHER_LOCATIONS = (
    "Brasilia|DF|Distrito Federal;"
    "Sao Paulo|SP|Sao Paulo;"
    "Rio de Janeiro|RJ|Rio de Janeiro;"
    "Belo Horizonte|MG|Minas Gerais;"
    "Salvador|BA|Bahia;"
    "Curitiba|PR|Parana;"
    "Porto Alegre|RS|Rio Grande do Sul;"
    "Recife|PE|Pernambuco;"
    "Manaus|AM|Amazonas;"
    "Belem|PA|Para"
)


@dataclass(frozen=True)
class Settings:
    """Configuracoes simples para bootstrap da API."""

    app_name: str = os.getenv("BACKEND_APP_NAME", "Nexus AI Portal Backend")
    app_version: str = os.getenv("BACKEND_APP_VERSION", "0.1.0")
    app_description: str = (
        "API inicial do portal de noticias, separada da camada do pipeline."
    )
    api_prefix: str = os.getenv("BACKEND_API_PREFIX", "/api/v1")
    api_host: str = os.getenv("BACKEND_API_HOST", "127.0.0.1")
    api_port: int = int(os.getenv("BACKEND_API_PORT", "8000"))
    cors_allowed_origins: tuple[str, ...] = (
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    )
    cors_allow_credentials: bool = True
    resend_api_key: str = os.getenv("RESEND_API_KEY", "").strip()
    resend_api_url: str = os.getenv("RESEND_API_URL", "https://api.resend.com/emails").strip()
    email_from_address: str = os.getenv("EMAIL_FROM_ADDRESS", "").strip()
    email_from_name: str = os.getenv("EMAIL_FROM_NAME", "Nexus IA").strip()
    email_reply_to: str = os.getenv("EMAIL_REPLY_TO", "").strip()
    frontend_reset_password_url: str = os.getenv(
        "FRONTEND_RESET_PASSWORD_URL",
        "http://localhost:5173/#reset-password",
    ).strip()
    weather_request_timeout_seconds: int = int(os.getenv("WEATHER_REQUEST_TIMEOUT_SECONDS", "15"))
    weather_cptec_timeout_seconds: int = int(os.getenv("WEATHER_CPTEC_TIMEOUT_SECONDS", "4"))
    weather_forecast_ttl_minutes: int = int(os.getenv("WEATHER_FORECAST_TTL_MINUTES", "180"))
    weather_alert_ttl_minutes: int = int(os.getenv("WEATHER_ALERT_TTL_MINUTES", "30"))
    weather_cptec_base_url: str = os.getenv("WEATHER_CPTEC_BASE_URL", "https://servicos.cptec.inpe.br/XML").strip()
    weather_inmet_alerts_url: str = os.getenv(
        "WEATHER_INMET_ALERTS_URL",
        "https://apiprevmet3.inmet.gov.br/avisos/rss/",
    ).strip()
    weather_openweather_api_key: str = os.getenv("WEATHER_OPENWEATHER_API_KEY", "").strip()
    weather_openweather_forecast_url: str = os.getenv(
        "WEATHER_OPENWEATHER_FORECAST_URL",
        "https://api.openweathermap.org/data/2.5/forecast",
    ).strip()
    weather_openmeteo_forecast_url: str = os.getenv(
        "WEATHER_OPENMETEO_FORECAST_URL",
        "https://api.open-meteo.com/v1/forecast",
    ).strip()
    weather_openmeteo_geocoding_url: str = os.getenv(
        "WEATHER_OPENMETEO_GEOCODING_URL",
        "https://geocoding-api.open-meteo.com/v1/search",
    ).strip()
    weather_default_locations: str = os.getenv("WEATHER_DEFAULT_LOCATIONS", DEFAULT_WEATHER_LOCATIONS).strip()


settings = Settings()
