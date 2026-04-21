"""Servicos agregados da camada config para o frontend."""

from backend.articles.article_read_schema import ArticleCardResponse
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


def _get_card_category_id(article: ArticleCardResponse) -> int | None:
    """Extrai o id da categoria associada ao card."""
    return article.category.id if article.category is not None else None


def _pick_watch_article(
    articles: list[ArticleCardResponse],
    *,
    excluded_ids: set[int],
) -> ArticleCardResponse | None:
    """Escolhe o melhor card para a faixa inferior, priorizando imagem."""
    available_articles = [article for article in articles if article.id not in excluded_ids]
    if not available_articles:
        return None

    article_with_image = next(
        (article for article in available_articles if article.image_url),
        None,
    )
    return article_with_image or available_articles[0]


def get_home() -> HomeResponse:
    """Monta os principais blocos da home usando apenas artigos publicados."""
    latest_articles = article_repository.list_published(limit=HOME_LATEST_ARTICLES_LIMIT, offset=0)
    latest_article_cards = [build_article_card(article) for article in latest_articles]
    used_article_ids = {article.id for article in latest_article_cards}
    used_watch_category_ids: set[int] = set()
    watch_articles: list[ArticleCardResponse] = []

    featured_categories = []
    for category_slug in CATEGORY_ORDER:
        category_detail = get_read_category(
            category_slug,
            limit=HOME_CATEGORY_ARTICLES_LIMIT,
            offset=0,
        )
        if category_detail is not None and category_detail.articles:
            selected_watch_article = _pick_watch_article(
                category_detail.articles,
                excluded_ids=used_article_ids,
            )
            if selected_watch_article is not None and len(watch_articles) < HOME_WATCH_ARTICLES_LIMIT:
                watch_articles.append(selected_watch_article)
                used_article_ids.add(selected_watch_article.id)
                selected_category_id = _get_card_category_id(selected_watch_article)
                if selected_category_id is not None:
                    used_watch_category_ids.add(selected_category_id)

            if len(featured_categories) < HOME_FEATURED_CATEGORY_LIMIT:
                featured_categories.append(category_detail)

    if len(watch_articles) < HOME_WATCH_ARTICLES_LIMIT:
        remaining_articles = article_repository.list_published(limit=50, offset=0)
        remaining_cards = [build_article_card(article) for article in remaining_articles]
        cards_with_image = [
            article
            for article in remaining_cards
            if article.id not in used_article_ids
            and article.image_url
            and _get_card_category_id(article) not in used_watch_category_ids
        ]
        cards_without_image = [
            article
            for article in remaining_cards
            if article.id not in used_article_ids
            and not article.image_url
            and _get_card_category_id(article) not in used_watch_category_ids
        ]

        for article in [*cards_with_image, *cards_without_image]:
            watch_articles.append(article)
            used_article_ids.add(article.id)
            article_category_id = _get_card_category_id(article)
            if article_category_id is not None:
                used_watch_category_ids.add(article_category_id)
            if len(watch_articles) >= HOME_WATCH_ARTICLES_LIMIT:
                break

    return HomeResponse(
        latest_articles=latest_article_cards,
        watch_articles=watch_articles,
        featured_categories=featured_categories,
    )
