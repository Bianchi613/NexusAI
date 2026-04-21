"""Coletor de noticias vindas de API HTTP.

Este coletor e opcional: ele so executa quando `NEWS_API_KEY` estiver definida.
Assim como os demais coletores, o objetivo aqui e produzir `RawArticle`
padronizado para o restante do pipeline.
"""

from datetime import datetime
from typing import Any, List, Optional
from urllib.parse import urlparse

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from Engine.app.config import settings
from Engine.app.core.article_filters import (
    build_content_hash,
    collect_image_urls,
    collect_video_urls,
    is_article_candidate,
    normalize_url,
    sanitize_article_text,
)
from Engine.app.models import NewsSource, RawArticle


class NewsAPICollector:
    """Integra uma API de noticias baseada em HTTP/JSON."""

    def collect(self, session: Session) -> List[RawArticle]:
        """Executa a coleta por API, se a credencial estiver configurada."""
        raw_articles: List[RawArticle] = []
        if not settings.news_api_key:
            return raw_articles

        sources = session.scalars(
            select(NewsSource).where(NewsSource.is_active.is_(True), NewsSource.source_type == "api")
        ).all()

        if not sources:
            sources = [self._create_default_source(session)]

        for source in sources:
            raw_articles.extend(self._fetch_source_articles(source))

        return raw_articles

    def _create_default_source(self, session: Session) -> NewsSource:
        """Cria uma fonte `api` padrao quando ainda nao houver registro no banco."""
        source = NewsSource(
            name=settings.news_api_source_name,
            base_url=settings.news_api_url,
            source_type="api",
            is_active=True,
        )
        session.add(source)
        session.flush()
        return source

    def _fetch_source_articles(self, source: NewsSource) -> List[RawArticle]:
        """Baixa a resposta da API e converte cada item em `RawArticle`."""
        response = requests.get(
            source.base_url or settings.news_api_url,
            params=self._build_params(),
            headers={"X-Api-Key": settings.news_api_key},
            timeout=30,
        )
        response.raise_for_status()

        payload = response.json()
        articles = payload.get("articles", [])
        collected: List[RawArticle] = []

        for article in articles:
            raw_article = self._normalize_article(source.id, article)
            if raw_article is not None:
                collected.append(raw_article)

        return collected

    def _build_params(self) -> dict[str, Any]:
        """Monta os parametros HTTP conforme o endpoint configurado."""
        params: dict[str, Any] = {"pageSize": settings.news_api_page_size}
        path = urlparse(settings.news_api_url).path

        if "top-headlines" in path:
            if settings.news_api_country:
                params["country"] = settings.news_api_country
            if settings.news_api_query:
                params["q"] = settings.news_api_query
        else:
            params["q"] = settings.news_api_query or "technology"
            if settings.news_api_language:
                params["language"] = settings.news_api_language

        return params

    def _normalize_article(self, source_id: int, article: dict[str, Any]) -> Optional[RawArticle]:
        """Transforma o payload da API em um artigo bruto filtrado."""
        original_url = normalize_url(article.get("url"))
        original_title = sanitize_article_text(article.get("title"))
        original_description = sanitize_article_text(article.get("description"))
        original_content = sanitize_article_text(article.get("content"))
        original_author = sanitize_article_text(article.get("author"))
        image_urls = collect_image_urls(
            article.get("urlToImage"),
            article.get("image"),
            article.get("images"),
            article.get("media"),
            article.get("enclosures"),
        )
        video_urls = collect_video_urls(
            article.get("video"),
            article.get("videoUrl"),
            article.get("videos"),
            article.get("media"),
            article.get("enclosures"),
        )

        if not is_article_candidate(
            original_title,
            original_description,
            original_content,
            original_url,
            blocked_terms=settings.blocked_title_terms,
            blocked_prefixes=settings.blocked_title_prefixes,
            min_title_length=settings.min_title_length,
            min_content_length=settings.min_content_length,
            min_quality_score=settings.min_quality_score,
        ):
            return None

        published_at = self._parse_datetime(article.get("publishedAt"))
        content_hash = build_content_hash(original_url, original_title, original_content or original_description)

        return RawArticle(
            source_id=source_id,
            external_id=original_url,
            original_title=original_title,
            original_url=original_url,
            original_description=original_description,
            original_content=original_content,
            original_author=original_author,
            original_image_url=image_urls[0] if image_urls else None,
            original_image_urls=image_urls,
            original_video_urls=video_urls,
            published_at=published_at,
            content_hash=content_hash,
        )

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Converte timestamps ISO8601 usados pela API."""
        if not value:
            return None

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
