"""Coletor de fontes no formato JSON Feed.

O fluxo e equivalente ao do RSS, mas adaptado para feeds JSON:
- registra fontes configuradas no `.env`
- baixa o payload de cada feed
- mapeia campos padrao para `RawArticle`
- preserva imagens e videos encontrados em anexos e HTML
"""

from datetime import datetime
from typing import Any, List, Optional

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from Engine.app.config import settings
from Engine.app.core.article_filters import (
    build_content_hash,
    collect_image_urls,
    collect_video_urls,
    extract_image_urls_from_html,
    extract_video_urls_from_html,
    is_article_candidate,
    normalize_url,
    sanitize_article_text,
)
from Engine.app.models import NewsSource, RawArticle


class JSONFeedCollector:
    """Coleta e normaliza noticias vindas de JSON Feed."""

    def collect(self, session: Session) -> List[RawArticle]:
        """Percorre todas as fontes JSON Feed ativas e coleta seus itens."""
        self._ensure_default_sources(session)
        sources = session.scalars(
            select(NewsSource).where(NewsSource.is_active.is_(True), NewsSource.source_type == "json_feed")
        ).all()

        raw_articles: List[RawArticle] = []
        for source in sources:
            raw_articles.extend(self._fetch_source_articles(source))

        return raw_articles

    def _ensure_default_sources(self, session: Session) -> None:
        """Sincroniza as fontes JSON Feed do `.env` com `news_sources`."""
        configured_feeds = list(settings.json_default_feeds)

        for name, url in configured_feeds:
            source = session.scalar(select(NewsSource).where(NewsSource.base_url == url))
            if source is not None:
                continue

            session.add(
                NewsSource(
                    name=name,
                    base_url=url,
                    source_type="json_feed",
                    is_active=True,
                )
            )

        session.flush()

    def _fetch_source_articles(self, source: NewsSource) -> List[RawArticle]:
        """Baixa o JSON do feed e tenta normalizar os itens retornados."""
        try:
            response = requests.get(
                source.base_url,
                timeout=30,
                headers={"User-Agent": "NexusAI/1.0", "Accept": "application/feed+json, application/json"},
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return []

        items = payload.get("items", [])
        collected: List[RawArticle] = []

        for item in items[: settings.json_feed_page_size]:
            raw_article = self._normalize_item(source.id, item)
            if raw_article is not None:
                collected.append(raw_article)

        return collected

    def _normalize_item(self, source_id: int, item: dict[str, Any]) -> Optional[RawArticle]:
        """Transforma um item JSON Feed em `RawArticle` filtrado."""
        title = sanitize_article_text(item.get("title"))
        url = normalize_url(item.get("url") or item.get("external_url"))
        summary = sanitize_article_text(item.get("summary"))
        content_html = item.get("content_html")
        content_text = item.get("content_text")
        content = sanitize_article_text(content_text or content_html)
        author = self._extract_author(item)
        external_id = sanitize_article_text(item.get("id")) or url
        published_at = self._parse_datetime(item.get("date_published") or item.get("date_modified"))
        image_urls = collect_image_urls(
            item.get("image"),
            item.get("banner_image"),
            self._extract_attachment_images(item.get("attachments")),
            extract_image_urls_from_html(content_html),
        )
        video_urls = collect_video_urls(
            item.get("video"),
            self._extract_attachment_videos(item.get("attachments")),
            extract_video_urls_from_html(content_html),
        )

        if not is_article_candidate(
            title,
            summary,
            content,
            url,
            blocked_terms=settings.blocked_title_terms,
            blocked_prefixes=settings.blocked_title_prefixes,
            min_title_length=settings.min_title_length,
            min_content_length=settings.min_content_length,
            min_quality_score=settings.min_quality_score,
        ):
            return None

        return RawArticle(
            source_id=source_id,
            external_id=external_id,
            original_title=title,
            original_url=url,
            original_description=summary,
            original_content=content,
            original_author=author,
            original_image_url=image_urls[0] if image_urls else None,
            original_image_urls=image_urls,
            original_video_urls=video_urls,
            published_at=published_at,
            content_hash=build_content_hash(url, title, content or summary),
        )

    def _extract_attachment_images(self, attachments: Any) -> list[str]:
        """Coleta imagens a partir de anexos tipados como image/*."""
        if not isinstance(attachments, list):
            return []

        image_urls: list[str] = []
        for attachment in attachments:
            if not isinstance(attachment, dict):
                continue
            mime_type = str(attachment.get("mime_type") or "").lower()
            if mime_type.startswith("image/"):
                image_urls.extend(collect_image_urls(attachment.get("url")))

        return image_urls

    def _extract_attachment_videos(self, attachments: Any) -> list[str]:
        """Coleta videos a partir de anexos tipados como video/*."""
        if not isinstance(attachments, list):
            return []

        video_urls: list[str] = []
        for attachment in attachments:
            if not isinstance(attachment, dict):
                continue
            mime_type = str(attachment.get("mime_type") or "").lower()
            if mime_type.startswith("video/"):
                video_urls.extend(collect_video_urls(attachment.get("url")))

        return video_urls

    def _extract_author(self, item: dict[str, Any]) -> Optional[str]:
        """Normaliza autor simples ou lista de autores do JSON Feed."""
        author = sanitize_article_text(item.get("author"))
        if author:
            return author

        authors = item.get("authors")
        if isinstance(authors, list):
            names = [sanitize_article_text(author_data.get("name")) for author_data in authors if isinstance(author_data, dict)]
            names = [name for name in names if name]
            if names:
                return ", ".join(names)

        return None

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Converte datas ISO8601 do JSON Feed."""
        if not value:
            return None

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
