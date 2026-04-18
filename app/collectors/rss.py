import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Optional

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import NewsSource, RawArticle


class RSSCollector:
    def collect(self, session: Session) -> List[RawArticle]:
        sources = session.scalars(
            select(NewsSource).where(NewsSource.is_active.is_(True), NewsSource.source_type == "rss")
        ).all()

        if not sources:
            sources = [self._get_or_create_default_source(session)]

        raw_articles: List[RawArticle] = []
        for source in sources:
            raw_articles.extend(self._fetch_source_articles(source))

        return raw_articles

    def _get_or_create_default_source(self, session: Session) -> NewsSource:
        source = session.scalar(
            select(NewsSource).where(NewsSource.base_url == settings.rss_default_feed_url)
        )
        if source is not None:
            return source

        source = NewsSource(
            name=settings.rss_default_source_name,
            base_url=settings.rss_default_feed_url,
            source_type="rss",
            is_active=True,
        )
        session.add(source)
        session.flush()
        return source

    def _fetch_source_articles(self, source: NewsSource) -> List[RawArticle]:
        response = requests.get(source.base_url, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        items = root.findall("./channel/item")

        collected: List[RawArticle] = []
        for item in items[: settings.rss_page_size]:
            raw_article = self._normalize_item(source.id, item)
            if raw_article is not None:
                collected.append(raw_article)

        return collected

    def _normalize_item(self, source_id: int, item: ET.Element) -> Optional[RawArticle]:
        title = self._text(item.find("title"))
        url = self._text(item.find("link"))
        description = self._text(item.find("description"))
        author = self._text(item.find("author")) or self._text(item.find("{http://purl.org/dc/elements/1.1/}creator"))
        external_id = self._text(item.find("guid")) or url
        published_at = self._parse_datetime(self._text(item.find("pubDate")))

        content = description or title
        if not title or not url:
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
            content_hash=self._build_content_hash(url, title, content),
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

    def _build_content_hash(self, original_url: str, title: str, content: Optional[str]) -> str:
        base = f"{original_url}|{title}|{content or ''}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()
