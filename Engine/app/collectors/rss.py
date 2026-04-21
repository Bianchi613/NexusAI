"""Coletor de noticias no formato RSS/XML.

Responsabilidades:
- garantir que as fontes RSS do `.env` existam em `news_sources`
- baixar cada feed ativo
- converter cada item em `RawArticle`
- separar midias de imagem e video ja no momento da coleta
"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Optional
from urllib.parse import urljoin

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
    is_probable_image_url,
    is_probable_video_url,
    is_article_candidate,
    normalize_url,
    sanitize_article_text,
)
from Engine.app.models import NewsSource, RawArticle


class RSSCollector:
    """Implementa a coleta de fontes RSS registradas no banco."""

    PAGE_IMAGE_META_PATTERNS = (
        re.compile(r"""<meta[^>]+property=["']og:image(?:url)?["'][^>]+content=["']([^"']+)["']""", re.IGNORECASE),
        re.compile(r"""<meta[^>]+name=["']twitter:image(?::src)?["'][^>]+content=["']([^"']+)["']""", re.IGNORECASE),
    )
    PAGE_VIDEO_META_PATTERNS = (
        re.compile(r"""<meta[^>]+property=["']og:video(?::url)?["'][^>]+content=["']([^"']+)["']""", re.IGNORECASE),
        re.compile(r"""<meta[^>]+name=["']twitter:player["'][^>]+content=["']([^"']+)["']""", re.IGNORECASE),
    )
    GENERIC_IMAGE_FRAGMENTS = (
        "logo",
        "favicon",
        "sprite",
        "icon",
        "avatar",
        "header-logo",
        "apple-touch",
        "site-logo",
        "branding",
    )
    GENERIC_VIDEO_FRAGMENTS = (
        "googletagmanager",
        "about:blank",
        "doubleclick",
        "analytics",
        "comentarios/pagina",
    )

    def collect(self, session: Session) -> List[RawArticle]:
        """Coleta todos os artigos das fontes RSS ativas."""
        self._ensure_default_sources(session)
        sources = session.scalars(
            select(NewsSource).where(NewsSource.is_active.is_(True), NewsSource.source_type == "rss")
        ).all()
        if settings.pipeline_test_mode:
            sources = sources[: max(1, settings.pipeline_test_sources_per_type)]

        raw_articles: List[RawArticle] = []
        for source in sources:
            raw_articles.extend(self._fetch_source_articles(source))

        return raw_articles

    def _ensure_default_sources(self, session: Session) -> None:
        """Sincroniza as fontes RSS do `.env` com a tabela `news_sources`."""
        configured_feeds = list(settings.rss_default_feeds)

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
        """Baixa e normaliza os itens de um feed RSS especifico."""
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

        item_limit = settings.rss_page_size
        if settings.pipeline_test_mode:
            item_limit = min(item_limit, max(1, settings.pipeline_test_items_per_feed))

        collected: List[RawArticle] = []
        for item in items[:item_limit]:
            raw_article = self._normalize_item(source.id, item)
            if raw_article is not None:
                collected.append(raw_article)

        return collected

    def _normalize_item(self, source_id: int, item: ET.Element) -> Optional[RawArticle]:
        """Transforma um `<item>` RSS em `RawArticle` filtrado."""
        title = sanitize_article_text(self._text_by_local_name(item, "title"))
        url = normalize_url(self._text_by_local_name(item, "link"))
        raw_description = self._text_by_local_name(item, "description")
        description = sanitize_article_text(raw_description)
        author = sanitize_article_text(
            self._text_by_local_name(item, "author") or self._text_by_local_name(item, "creator")
        )
        external_id = self._text_by_local_name(item, "guid") or url
        published_at = self._parse_datetime(self._text_by_local_name(item, "pubDate"))
        image_urls = self._extract_image_urls(item, raw_description)
        video_urls = self._extract_video_urls(item, raw_description)
        if url and (not image_urls or not video_urls):
            image_urls, video_urls = self._enrich_media_from_article_page(url, image_urls, video_urls)

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
            original_image_url=image_urls[0] if image_urls else None,
            original_image_urls=image_urls,
            original_video_urls=video_urls,
            published_at=published_at,
            content_hash=build_content_hash(url, title, content),
        )

    def _text(self, node: Optional[ET.Element]) -> Optional[str]:
        """Le texto simples de um no XML, quando existir."""
        if node is None or node.text is None:
            return None
        value = node.text.strip()
        return value or None

    def _local_name(self, tag: str) -> str:
        """Extrai apenas o nome local da tag, sem namespace."""
        return tag.split("}", 1)[-1] if "}" in tag else tag

    def _children_by_local_name(self, item: ET.Element, *names: str) -> list[ET.Element]:
        """Busca filhos imediatos comparando apenas o nome local das tags."""
        accepted_names = set(names)
        return [child for child in list(item) if self._local_name(child.tag) in accepted_names]

    def _first_child_by_local_name(self, item: ET.Element, *names: str) -> Optional[ET.Element]:
        """Retorna o primeiro filho cujo nome local combine."""
        nodes = self._children_by_local_name(item, *names)
        return nodes[0] if nodes else None

    def _text_by_local_name(self, item: ET.Element, *names: str) -> Optional[str]:
        """Le texto do primeiro filho compatível pelo nome local da tag."""
        return self._text(self._first_child_by_local_name(item, *names))

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Converte datas RFC822 de RSS para `datetime`."""
        if not value:
            return None
        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None

    def _sanitize_xml(self, content: bytes) -> bytes:
        """Corrige pequenas sujeiras de XML antes do parse."""
        return content.replace(b"&nbsp;", b" ").replace(b"\x00", b"")

    def _enrich_media_from_article_page(
        self,
        article_url: str,
        image_urls: list[str],
        video_urls: list[str],
    ) -> tuple[list[str], list[str]]:
        """Busca imagem e video na pagina original quando o feed vier incompleto."""
        page_image_urls, page_video_urls = self._extract_page_media(article_url)
        return collect_image_urls(image_urls, page_image_urls), collect_video_urls(video_urls, page_video_urls)

    def _extract_page_media(self, article_url: str) -> tuple[list[str], list[str]]:
        """Extrai midias diretamente do HTML da pagina original da noticia."""
        try:
            response = requests.get(
                article_url,
                timeout=20,
                headers={"User-Agent": "NexusAI/1.0"},
            )
            response.raise_for_status()
        except requests.RequestException:
            return [], []

        if not response.encoding:
            response.encoding = response.apparent_encoding or "utf-8"

        html = response.text or ""
        image_candidates: list[str] = []
        video_candidates: list[str] = []

        for pattern in self.PAGE_IMAGE_META_PATTERNS:
            image_candidates.extend(pattern.findall(html))
        for pattern in self.PAGE_VIDEO_META_PATTERNS:
            video_candidates.extend(pattern.findall(html))

        if not image_candidates:
            image_candidates.extend(extract_image_urls_from_html(html))
        if not video_candidates:
            video_candidates.extend(extract_video_urls_from_html(html))

        image_urls = collect_image_urls(self._resolve_page_urls(article_url, image_candidates, kind="image"))
        video_urls = collect_video_urls(self._resolve_page_urls(article_url, video_candidates, kind="video"))
        return image_urls, video_urls

    def _resolve_page_urls(self, article_url: str, urls: list[str], *, kind: str) -> list[str]:
        """Resolve URLs relativas e filtra midias genericas da pagina."""
        resolved_urls: list[str] = []

        for url in urls:
            resolved_url = normalize_url(urljoin(article_url, (url or "").strip()))
            if not resolved_url:
                continue
            if kind == "image" and self._is_useful_page_image(resolved_url):
                resolved_urls.append(resolved_url)
            if kind == "video" and self._is_useful_page_video(resolved_url):
                resolved_urls.append(resolved_url)

        return resolved_urls

    def _is_useful_page_image(self, url: str) -> bool:
        """Descarta imagens tecnicas ou de layout e preserva a imagem editorial."""
        lowered = url.lower()
        if not is_probable_image_url(url):
            return False
        return not any(fragment in lowered for fragment in self.GENERIC_IMAGE_FRAGMENTS)

    def _is_useful_page_video(self, url: str) -> bool:
        """Descarta iframes tecnicos e preserva videos reais da materia."""
        lowered = url.lower()
        if not is_probable_video_url(url):
            return False
        return not any(fragment in lowered for fragment in self.GENERIC_VIDEO_FRAGMENTS)

    def _extract_image_urls(self, item: ET.Element, raw_description: Optional[str]) -> list[str]:
        """Extrai imagens de `enclosure`, tags de midia e HTML embutido."""
        collected: list[str] = []

        for enclosure in self._children_by_local_name(item, "enclosure"):
            mime_type = (enclosure.get("type") or "").lower()
            url = enclosure.get("url")
            if mime_type.startswith("image/") or is_probable_image_url(url):
                collected.extend(collect_image_urls(url))

        for node in self._children_by_local_name(item, "content", "thumbnail"):
            medium = (node.get("medium") or "").lower()
            mime_type = (node.get("type") or "").lower()
            url = node.get("url")
            if medium == "image" or mime_type.startswith("image/") or is_probable_image_url(url):
                collected.extend(collect_image_urls(url))

        if raw_description:
            collected.extend(extract_image_urls_from_html(raw_description))

        return collect_image_urls(collected)

    def _extract_video_urls(self, item: ET.Element, raw_description: Optional[str]) -> list[str]:
        """Extrai videos de `enclosure`, tags de midia e HTML embutido."""
        collected: list[str] = []

        for enclosure in self._children_by_local_name(item, "enclosure"):
            mime_type = (enclosure.get("type") or "").lower()
            url = enclosure.get("url")
            if mime_type.startswith("video/") or is_probable_video_url(url):
                collected.extend(collect_video_urls(url))

        for node in self._children_by_local_name(item, "content", "player"):
            medium = (node.get("medium") or "").lower()
            mime_type = (node.get("type") or "").lower()
            url = node.get("url")
            if medium == "video" or mime_type.startswith("video/") or is_probable_video_url(url):
                collected.extend(collect_video_urls(url))

        if raw_description:
            collected.extend(extract_video_urls_from_html(raw_description))

        return collect_video_urls(collected)
