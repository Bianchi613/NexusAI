import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback para ambiente sem dependencia instalada
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"Variavel de ambiente obrigatoria ausente: {name}")
    return value


def _normalize_database_url(value: str) -> str:
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "NexusAI")
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = _normalize_database_url(_require_env("DATABASE_URL"))
    database_echo: bool = _as_bool(os.getenv("DATABASE_ECHO"), default=False)
    ollama_model: str = _require_env("OLLAMA_MODEL")
    ollama_base_url: str = _require_env("OLLAMA_BASE_URL")
    news_api_key: Optional[str] = os.getenv("NEWS_API_KEY")
    news_api_url: str = os.getenv("NEWS_API_URL", "https://newsapi.org/v2/top-headlines")
    news_api_country: str = os.getenv("NEWS_API_COUNTRY", "us")
    news_api_language: str = os.getenv("NEWS_API_LANGUAGE", "en")
    news_api_query: Optional[str] = os.getenv("NEWS_API_QUERY")
    news_api_page_size: int = int(os.getenv("NEWS_API_PAGE_SIZE", "10"))
    rss_default_feed_url: str = os.getenv("RSS_DEFAULT_FEED_URL", "https://www.nasa.gov/feed/")
    rss_default_source_name: str = os.getenv("RSS_DEFAULT_SOURCE_NAME", "NASA RSS")
    rss_page_size: int = int(os.getenv("RSS_PAGE_SIZE", "10"))
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))


settings = Settings()
