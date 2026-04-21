"""Configuracoes basicas da API do portal."""

import os
from dataclasses import dataclass


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


settings = Settings()
