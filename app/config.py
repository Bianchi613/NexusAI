import os
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

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
        normalized = value.replace("postgresql://", "postgresql+psycopg://", 1)
        parts = urlsplit(normalized)
        if parts.hostname == "localhost":
            netloc = parts.netloc.replace("localhost", "127.0.0.1", 1)
            return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
        return normalized
    return value


def _parse_csv(value: Optional[str], default: str = "") -> list[str]:
    raw_value = value if value is not None else default
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _parse_feed_entries(value: Optional[str], default: str = "") -> list[tuple[str, str]]:
    raw_value = value if value is not None else default
    entries: list[tuple[str, str]] = []

    for chunk in raw_value.split(";"):
        item = chunk.strip()
        if not item or "|" not in item:
            continue

        name, url = item.split("|", 1)
        name = name.strip()
        url = url.strip()
        if name and url:
            entries.append((name, url))

    return entries


@dataclass
class Settings:
    # App
    app_name: str = os.getenv("APP_NAME", "NexusAI")
    app_env: str = os.getenv("APP_ENV", "development")

    # Database
    database_url: str = _normalize_database_url(_require_env("DATABASE_URL"))
    database_echo: bool = _as_bool(os.getenv("DATABASE_ECHO"), default=False)

    # AI
    ollama_model: str = _require_env("OLLAMA_MODEL")
    ollama_base_url: str = _require_env("OLLAMA_BASE_URL")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))

    # API
    news_api_key: Optional[str] = os.getenv("NEWS_API_KEY")
    news_api_source_name: str = os.getenv("NEWS_API_SOURCE_NAME", "NewsAPI")
    news_api_url: str = os.getenv("NEWS_API_URL", "https://newsapi.org/v2/top-headlines")
    news_api_country: str = os.getenv("NEWS_API_COUNTRY", "us")
    news_api_language: str = os.getenv("NEWS_API_LANGUAGE", "en")
    news_api_query: Optional[str] = os.getenv("NEWS_API_QUERY")
    news_api_page_size: int = int(os.getenv("NEWS_API_PAGE_SIZE", "10"))

    # RSS
    rss_page_size: int = int(os.getenv("RSS_PAGE_SIZE", "10"))
    rss_default_feeds: list[tuple[str, str]] = field(
        default_factory=lambda: _parse_feed_entries(
            os.getenv("RSS_DEFAULT_FEEDS"),
            "",
        )
    )

    # JSON Feed
    json_feed_page_size: int = int(os.getenv("JSON_FEED_PAGE_SIZE", "10"))
    json_default_feeds: list[tuple[str, str]] = field(
        default_factory=lambda: _parse_feed_entries(
            os.getenv("JSON_DEFAULT_FEEDS"),
            "",
        )
    )

    # Pipeline
    pipeline_max_items_per_run: int = int(os.getenv("PIPELINE_MAX_ITEMS_PER_RUN", "12"))
    pipeline_candidate_pool_multiplier: int = int(os.getenv("PIPELINE_CANDIDATE_POOL_MULTIPLIER", "1"))
    pipeline_generation_buffer: int = int(os.getenv("PIPELINE_GENERATION_BUFFER", "4"))
    max_raw_articles_per_source: int = int(os.getenv("MAX_RAW_ARTICLES_PER_SOURCE", "3"))
    max_articles_per_source_per_run: int = int(os.getenv("MAX_ARTICLES_PER_SOURCE_PER_RUN", "3"))
    max_articles_per_category_per_run: int = int(os.getenv("MAX_ARTICLES_PER_CATEGORY_PER_RUN", "2"))
    min_distinct_categories_per_run: int = int(os.getenv("MIN_DISTINCT_CATEGORIES_PER_RUN", "2"))
    deduplication_lookback_days: int = int(os.getenv("DEDUPLICATION_LOOKBACK_DAYS", "15"))

    # Filters
    min_title_length: int = int(os.getenv("MIN_TITLE_LENGTH", "20"))
    min_content_length: int = int(os.getenv("MIN_CONTENT_LENGTH", "40"))
    min_quality_score: int = int(os.getenv("MIN_QUALITY_SCORE", "1"))
    blocked_title_terms: list[str] = field(
        default_factory=lambda: _parse_csv(
            os.getenv("BLOCKED_TITLE_TERMS"),
            "webinar,sponsored,advertisement,press release",
        )
    )
    blocked_title_prefixes: list[str] = field(
        default_factory=lambda: _parse_csv(
            os.getenv("BLOCKED_TITLE_PREFIXES"),
            "saiba como,confira,entenda como,veja como",
        )
    )
    allowed_categories: list[str] = field(
        default_factory=lambda: _parse_csv(
            os.getenv("ALLOWED_CATEGORIES"),
            "Geral,Tecnologia,Ciencia,Espaco,Negocios,Politica,Saude,Esportes",
        )
    )
    max_tags_per_article: int = int(os.getenv("MAX_TAGS_PER_ARTICLE", "5"))


settings = Settings()
