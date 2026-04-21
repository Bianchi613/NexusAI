"""Controller das rotas de leitura de categorias."""

from fastapi import HTTPException, status

from backend.articles.article_read_schema import ArticleReadListResponse
from backend.categories.category_read_schema import CategoryReadDetailResponse, CategoryReadSummary
from backend.categories.category_read_service import (
    get_read_category,
    list_read_categories,
    list_read_category_articles,
)


def list_read_categories_controller() -> list[CategoryReadSummary]:
    """Lista categorias visiveis ao frontend."""
    return list_read_categories()


def get_read_category_controller(
    category_slug: str,
    *,
    limit: int,
    offset: int,
) -> CategoryReadDetailResponse:
    """Retorna uma categoria ou 404."""
    category = get_read_category(category_slug, limit=limit, offset=offset)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada.",
        )
    return category


def list_read_category_articles_controller(
    category_slug: str,
    *,
    limit: int,
    offset: int,
) -> ArticleReadListResponse:
    """Retorna os artigos de uma categoria ou 404."""
    articles = list_read_category_articles(category_slug, limit=limit, offset=offset)
    if articles is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada.",
        )
    return articles
