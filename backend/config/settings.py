"""Configuracoes basicas da API do portal."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Configuracoes simples para bootstrap da API."""

    app_name: str = "Nexus AI Portal Backend"
    app_version: str = "0.1.0"
    app_description: str = (
        "API inicial do portal de noticias, separada da camada do pipeline."
    )
    api_prefix: str = "/api/v1"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_allowed_origins: tuple[str, ...] = (
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    )
    cors_allow_credentials: bool = True


settings = Settings()
