"""Servico de leitura de artigos publicados para o frontend."""

from __future__ import annotations

import math
import re
import unicodedata
from collections.abc import Iterable

from app.core.article_filters import slugify, truncate_text
from backend.articles.article_read_schema import (
    ArticleCardResponse,
    ArticleReadDetailResponse,
    ArticleReadListResponse,
    ArticleSourceReadItem,
    TagReadItem,
)
from backend.articles.article_repository import ArticleRepository
from backend.config.editorial_config import build_category_summary
from backend.tags.tag_repository import TagRepository


article_repository = ArticleRepository()
tag_repository = TagRepository()


def build_virtual_article_slug(*, article_id: int, title: str) -> str:
    """Gera um slug estavel sem precisar persisti-lo no banco."""
    return f"{slugify(title or f'artigo-{article_id}')}-{article_id}"


def parse_virtual_article_slug(article_slug: str) -> int | None:
    """Extrai o id do artigo a partir do slug virtual."""
    match = re.search(r"(\d+)$", article_slug.strip())
    if match is None:
        return None
    return int(match.group(1))


def _calculate_read_time_minutes(body: str) -> int:
    """Estima o tempo de leitura a partir do corpo do artigo."""
    words = len(re.findall(r"\w+", body or ""))
    return max(1, math.ceil(words / 180))


def _split_body_paragraphs(body: str) -> list[str]:
    """Quebra o corpo em paragrafos simples para o frontend."""
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n+", (body or "").strip()) if paragraph.strip()]
    if paragraphs:
        return paragraphs
    cleaned_body = (body or "").strip()
    return [cleaned_body] if cleaned_body else []


def _normalize_search_value(value: str = "") -> str:
    """Normaliza texto para comparacao simples na busca publica."""
    normalized = unicodedata.normalize("NFD", (value or "").lower())
    without_accents = "".join(character for character in normalized if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", " ", without_accents).strip()


def _resolve_tags(tag_ids: Iterable[int]) -> list[TagReadItem]:
    """Resolve ids de tags em objetos publicos."""
    resolved_tags: list[TagReadItem] = []
    for tag in tag_repository.list_by_ids(list(tag_ids)):
        resolved_tags.append(TagReadItem(id=tag.id, name=tag.name, slug=tag.slug))
    return resolved_tags


def _derive_author(article) -> str:
    """Escolhe um autor publico seguro."""
    reviewer = getattr(article, "reviewer", None)
    if reviewer is not None and getattr(reviewer, "name", None):
        return reviewer.name
    return "Redacao Nexus IA"


def _derive_label(article, tags: list[TagReadItem]) -> str:
    """Escolhe uma label curta para o card."""
    if tags:
        return tags[0].name
    if article.category is not None and getattr(article.category, "name", None):
        return build_category_summary(article.category).name
    return "Portal"


def _resolve_source_articles(article) -> list[ArticleSourceReadItem]:
    """Converte vinculos de fontes brutas em itens publicos para a pagina da materia."""
    source_items: list[ArticleSourceReadItem] = []

    for source_link in list(getattr(article, "raw_article_links", []) or []):
        raw_article = getattr(source_link, "raw_article", None)
        if raw_article is None or not getattr(raw_article, "original_url", None):
            continue

        source = getattr(raw_article, "source", None)
        source_items.append(
            ArticleSourceReadItem(
                raw_article_id=raw_article.id,
                source_name=getattr(source, "name", None),
                original_title=raw_article.original_title,
                original_url=raw_article.original_url,
                original_author=raw_article.original_author,
            )
        )

    return source_items


def build_article_card(article) -> ArticleCardResponse:
    """Converte um artigo ORM em card de leitura."""
    tags = _resolve_tags(list(article.tags or []))
    image_urls = list(article.image_urls or [])
    video_urls = list(article.video_urls or [])
    summary = article.summary or truncate_text(article.body, 220)

    return ArticleCardResponse(
        id=article.id,
        slug=build_virtual_article_slug(article_id=article.id, title=article.title),
        title=article.title,
        summary=summary,
        excerpt=truncate_text(summary or article.body, 180),
        label=_derive_label(article, tags),
        category=build_category_summary(article.category) if article.category else None,
        author=_derive_author(article),
        published_at=article.published_at,
        read_time_minutes=_calculate_read_time_minutes(article.body),
        location="Brasil",
        image_url=image_urls[0] if image_urls else None,
        video_url=video_urls[0] if video_urls else None,
    )


def list_published_articles(*, limit: int, offset: int) -> ArticleReadListResponse:
    """Lista artigos publicados para a vitrine do frontend."""
    articles = article_repository.list_published(limit=limit + 1, offset=offset)
    has_more = len(articles) > limit
    return ArticleReadListResponse(
        items=[build_article_card(article) for article in articles[:limit]],
        limit=limit,
        offset=offset,
        has_more=has_more,
    )


def search_published_articles(*, query: str, limit: int) -> ArticleReadListResponse:
    """Realiza busca simples nas materias publicadas sem depender de alteracao de schema."""
    normalized_query = _normalize_search_value(query)
    if len(normalized_query) < 2:
        return ArticleReadListResponse(items=[], limit=limit, offset=0, has_more=False)

    search_window = max(120, limit * 20)
    articles = article_repository.list_published(limit=search_window, offset=0)
    matched_cards: list[ArticleCardResponse] = []

    for article in articles:
        card = build_article_card(article)
        searchable_content = _normalize_search_value(
            " ".join(
                [
                    card.title,
                    card.summary or "",
                    card.excerpt or "",
                    card.label,
                    card.category.name if card.category is not None else "",
                    card.category.slug if card.category is not None else "",
                ]
            )
        )

        if normalized_query not in searchable_content:
            continue

        matched_cards.append(card)
        if len(matched_cards) >= limit + 1:
            break

    has_more = len(matched_cards) > limit
    return ArticleReadListResponse(
        items=matched_cards[:limit],
        limit=limit,
        offset=0,
        has_more=has_more,
    )


def list_published_articles_by_category(
    *,
    category_id: int,
    limit: int,
    offset: int,
) -> ArticleReadListResponse:
    """Lista artigos publicados de uma categoria."""
    articles = article_repository.list_all(
        limit=limit + 1,
        offset=offset,
        status="publicada",
        category_id=category_id,
    )
    has_more = len(articles) > limit
    return ArticleReadListResponse(
        items=[build_article_card(article) for article in articles[:limit]],
        limit=limit,
        offset=offset,
        has_more=has_more,
    )


def get_published_article(article_slug: str) -> ArticleReadDetailResponse | None:
    """Busca um artigo publicado usando o slug virtual."""
    article_id = parse_virtual_article_slug(article_slug)
    if article_id is None:
        return None

    article = article_repository.get_published_by_id(article_id)
    if article is None:
        return None

    tags = _resolve_tags(list(article.tags or []))
    related_articles = article_repository.list_all(
        limit=4,
        offset=0,
        status="publicada",
        category_id=article.category_id,
    )
    related_cards = [
        build_article_card(related_article)
        for related_article in related_articles
        if related_article.id != article.id
    ][:3]

    return ArticleReadDetailResponse(
        id=article.id,
        slug=build_virtual_article_slug(article_id=article.id, title=article.title),
        title=article.title,
        summary=article.summary or truncate_text(article.body, 220),
        body=article.body,
        body_paragraphs=_split_body_paragraphs(article.body),
        label=_derive_label(article, tags),
        category=build_category_summary(article.category) if article.category else None,
        author=_derive_author(article),
        published_at=article.published_at,
        read_time_minutes=_calculate_read_time_minutes(article.body),
        location="Brasil",
        image_urls=list(article.image_urls or []),
        video_urls=list(article.video_urls or []),
        tags=tags,
        source_articles=_resolve_source_articles(article),
        related_articles=related_cards,
    )


def list_related_published_articles(article_slug: str, *, limit: int) -> list[ArticleCardResponse] | None:
    """Lista artigos relacionados a um artigo publicado."""
    article = get_published_article(article_slug)
    if article is None:
        return None
    return article.related_articles[:limit]
