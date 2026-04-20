"""Rotas publicas de artigos."""

from fastapi import APIRouter, Query

from backend.articles.article_controller import get_published_article, list_published_articles
from backend.articles.article_schema import ArticleDetailResponse, ArticleListItem


router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=list[ArticleListItem])
def list_articles(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ArticleListItem]:
    """Lista artigos publicados para o portal publico."""
    return list_published_articles(limit=limit, offset=offset)


@router.get("/{article_id}", response_model=ArticleDetailResponse)
def get_article(article_id: int) -> ArticleDetailResponse:
    """Retorna o detalhe de um artigo publicado."""
    return get_published_article(article_id)
