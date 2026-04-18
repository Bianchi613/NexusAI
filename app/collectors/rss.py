import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Optional

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.article_filters import build_content_hash, is_article_candidate, normalize_url, sanitize_article_text
from app.models import NewsSource, RawArticle


class RSSCollector:
    def collect(self, session: Session) -> List[RawArticle]:
        self._ensure_default_sources(session)
        sources = session.scalars(
            select(NewsSource).where(NewsSource.is_active.is_(True), NewsSource.source_type == "rss")
        ).all()

        raw_articles: List[RawArticle] = []
        for source in sources:
            raw_articles.extend(self._fetch_source_articles(source))

        return raw_articles

    def _ensure_default_sources(self, session: Session) -> None:
        configured_feeds = list(settings.rss_default_feeds)

        if not configured_feeds:
            configured_feeds = [(settings.rss_default_source_name, settings.rss_default_feed_url)]

        for name, url in configured_feeds:
            source = session.scalar(select(NewsSource).where(NewsSource.base_url == url))
            if source is not None:
                continue

            session.add(
                NewsSource(
                    name=name,
                    base_url=url,
                    source_type="rss",
                    is_active=True,
                )
            )

        session.flush()

    def _fetch_source_articles(self, source: NewsSource) -> List[RawArticle]:
        try:
            response = requests.get(
                source.base_url,
                timeout=30,
                headers={"User-Agent": "NexusAI/1.0"},
            )
            response.raise_for_status()
        except requests.RequestException:
            return []

        try:
            root = ET.fromstring(self._sanitize_xml(response.content))
        except ET.ParseError:
            return []

        items = root.findall("./channel/item")
        if not items:
            items = root.findall(".//item")

        collected: List[RawArticle] = []
        for item in items[: settings.rss_page_size]:
            raw_article = self._normalize_item(source.id, item)
            if raw_article is not None:
                collected.append(raw_article)

        return collected

    def _normalize_item(self, source_id: int, item: ET.Element) -> Optional[RawArticle]:
        title = self._text(item.find("title"))
        url = normalize_url(self._text(item.find("link")))
        description = sanitize_article_text(self._text(item.find("description")))
        author = sanitize_article_text(
            self._text(item.find("author")) or self._text(item.find("{http://purl.org/dc/elements/1.1/}creator"))
        )
        external_id = self._text(item.find("guid")) or url
        published_at = self._parse_datetime(self._text(item.find("pubDate")))

        content = description or title
        if not is_article_candidate(
            title,
            description,
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
            original_description=description,
            original_content=content,
            original_author=author,
            published_at=published_at,
            content_hash=build_content_hash(url, title, content),
        )

    def _text(self, node: Optional[ET.Element]) -> Optional[str]:
        if node is None or node.text is None:
            return None
        value = node.text.strip()
        return value or None

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None

    def _sanitize_xml(self, content: bytes) -> bytes:
        text = content.decode("utf-8", errors="replace")
        text = text.replace("&nbsp;", " ")
        return text.encode("utf-8")
