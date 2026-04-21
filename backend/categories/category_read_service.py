"""Servico de leitura de categorias para o frontend."""

from backend.articles.article_read_schema import ArticleReadListResponse
from backend.articles.article_read_service import build_article_card, list_published_articles_by_category
from backend.articles.article_repository import ArticleRepository
from backend.categories.category_read_schema import CategoryReadDetailResponse, CategoryReadSummary
from backend.config.editorial_config import (
    build_category_response,
    build_category_summary,
    category_sort_key,
    resolve_database_category_slug,
)
from backend.categories.category_repository import CategoryRepository


category_repository = CategoryRepository()
article_repository = ArticleRepository()


def _get_category_from_public_slug(category_slug: str):
    """Resolve uma categoria publica a partir do slug exposto na API."""
    database_slug = resolve_database_category_slug(category_slug)
    category = category_repository.find_by_slug(database_slug)
    if category is not None:
        return category
    if database_slug != category_slug:
        return category_repository.find_by_slug(category_slug)
    return None


def list_read_categories() -> list[CategoryReadSummary]:
    """Lista categorias com artigos publicados visiveis ao frontend."""
    categories = category_repository.list_all(limit=200, offset=0)
    visible_categories: list[CategoryReadSummary] = []

    for category in categories:
        published_articles = article_repository.list_all(
            limit=1,
            offset=0,
            status="publicada",
            category_id=category.id,
        )
        if not published_articles:
            continue
        visible_categories.append(build_category_summary(category))

    return sorted(visible_categories, key=category_sort_key)


def get_read_category(
    category_slug: str,
    *,
    limit: int,
    offset: int,
) -> CategoryReadDetailResponse | None:
    """Retorna uma categoria com sua vitrine de artigos publicados."""
    category = _get_category_from_public_slug(category_slug)
    if category is None:
        return None

    articles = article_repository.list_all(
        limit=limit + 1,
        offset=offset,
        status="publicada",
        category_id=category.id,
    )
    has_more = len(articles) > limit
    visible_articles = articles[:limit]
    article_cards = [build_article_card(article) for article in visible_articles]

    return CategoryReadDetailResponse(
        category=build_category_response(category),
        featured_article=article_cards[0] if article_cards else None,
        articles=article_cards,
        limit=limit,
        offset=offset,
        has_more=has_more,
    )


def list_read_category_articles(
    category_slug: str,
    *,
    limit: int,
    offset: int,
) -> ArticleReadListResponse | None:
    """Lista apenas os artigos publicados de uma categoria."""
    category = _get_category_from_public_slug(category_slug)
    if category is None:
        return None
    return list_published_articles_by_category(category_id=category.id, limit=limit, offset=offset)
