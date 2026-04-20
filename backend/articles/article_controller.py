"""Controller das rotas publicas de artigos."""

from fastapi import HTTPException, status

from backend.articles.article_schema import ArticleDetailResponse, ArticleListItem
from backend.articles.article_service import fetch_published_article, fetch_published_articles


def list_published_articles(limit: int, offset: int) -> list[ArticleListItem]:
    """Lista artigos publicados para o portal."""
    return fetch_published_articles(limit=limit, offset=offset)


def get_published_article(article_id: int) -> ArticleDetailResponse:
    """Retorna um artigo publicado ou 404."""
    article = fetch_published_article(article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artigo publicado nao encontrado.",
        )
    return article
