"""Servicos agregados da camada config para o frontend."""

from backend.articles.article_read_service import build_article_card
from backend.articles.article_repository import ArticleRepository
from backend.categories.category_read_service import get_read_category
from backend.config.config_schema import HomeResponse
from backend.config.editorial_config import (
    CATEGORY_ORDER,
    HOME_CATEGORY_ARTICLES_LIMIT,
    HOME_FEATURED_CATEGORY_LIMIT,
    HOME_LATEST_ARTICLES_LIMIT,
    HOME_WATCH_ARTICLES_LIMIT,
)


article_repository = ArticleRepository()


def get_home() -> HomeResponse:
    """Monta os principais blocos da home usando apenas artigos publicados."""
    latest_articles = article_repository.list_published(limit=HOME_LATEST_ARTICLES_LIMIT, offset=0)
    watch_articles = article_repository.list_published(
        limit=HOME_WATCH_ARTICLES_LIMIT,
        offset=HOME_LATEST_ARTICLES_LIMIT,
    )

    featured_categories = []
    for category_slug in CATEGORY_ORDER:
        category_detail = get_read_category(
            category_slug,
            limit=HOME_CATEGORY_ARTICLES_LIMIT,
            offset=0,
        )
        if category_detail is not None and category_detail.articles:
            featured_categories.append(category_detail)
        if len(featured_categories) >= HOME_FEATURED_CATEGORY_LIMIT:
            break

    return HomeResponse(
        latest_articles=[build_article_card(article) for article in latest_articles],
        watch_articles=[build_article_card(article) for article in watch_articles],
        featured_categories=featured_categories,
    )
