"""Controller das rotas de leitura de artigos."""

from fastapi import HTTPException, status

from backend.articles.article_read_schema import ArticleCardResponse, ArticleReadDetailResponse, ArticleReadListResponse
from backend.articles.article_read_service import (
    get_published_article,
    list_published_articles,
    list_related_published_articles,
    search_published_articles,
)


def list_published_articles_controller(*, limit: int, offset: int) -> ArticleReadListResponse:
    """Lista artigos publicados para a camada HTTP."""
    return list_published_articles(limit=limit, offset=offset)


def search_published_articles_controller(*, query: str, limit: int) -> ArticleReadListResponse:
    """Busca artigos publicados para a camada HTTP."""
    return search_published_articles(query=query, limit=limit)


def get_published_article_controller(article_slug: str) -> ArticleReadDetailResponse:
    """Retorna um artigo publicado ou 404."""
    article = get_published_article(article_slug)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artigo publicado nao encontrado.",
        )
    return article


def list_related_published_articles_controller(article_slug: str, *, limit: int) -> list[ArticleCardResponse]:
    """Retorna artigos relacionados ou 404."""
    related_articles = list_related_published_articles(article_slug, limit=limit)
    if related_articles is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artigo publicado nao encontrado.",
        )
    return related_articles
