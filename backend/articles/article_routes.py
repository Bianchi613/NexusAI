"""Rotas de artigos."""

from fastapi import APIRouter, Query, status

from backend.articles.article_controller import (
    create_portal_article,
    delete_portal_article,
    get_portal_article,
    list_portal_articles,
    update_portal_article,
)
from backend.articles.article_read_controller import (
    get_published_article_controller,
    list_published_articles_controller,
    list_related_published_articles_controller,
)
from backend.articles.article_read_schema import ArticleCardResponse, ArticleReadDetailResponse, ArticleReadListResponse
from backend.articles.article_schema import (
    ArticleCreateRequest,
    ArticleDetailResponse,
    ArticleListItem,
    ArticleUpdateRequest,
)


router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=list[ArticleListItem])
def list_articles_route(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: str | None = Query(default=None, alias="status"),
    category_id: int | None = Query(default=None, ge=1),
    reviewed_by: int | None = Query(default=None, ge=1),
) -> list[ArticleListItem]:
    """Lista artigos com filtros opcionais."""
    return list_portal_articles(
        limit=limit,
        offset=offset,
        status_filter=status_filter,
        category_id=category_id,
        reviewed_by=reviewed_by,
    )


@router.get("/published", response_model=ArticleReadListResponse)
def list_published_articles_route(
    limit: int = Query(default=12, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
) -> ArticleReadListResponse:
    """Lista artigos publicados para o frontend."""
    return list_published_articles_controller(limit=limit, offset=offset)


@router.get("/slug/{article_slug}/related", response_model=list[ArticleCardResponse])
def list_related_articles_route(
    article_slug: str,
    limit: int = Query(default=3, ge=1, le=10),
) -> list[ArticleCardResponse]:
    """Lista artigos relacionados a um artigo publicado."""
    return list_related_published_articles_controller(article_slug, limit=limit)


@router.get("/slug/{article_slug}", response_model=ArticleReadDetailResponse)
def get_published_article_route(article_slug: str) -> ArticleReadDetailResponse:
    """Retorna um artigo publicado pelo slug virtual."""
    return get_published_article_controller(article_slug)


@router.get("/{article_id}", response_model=ArticleDetailResponse)
def get_article_route(article_id: int) -> ArticleDetailResponse:
    """Retorna o detalhe de um artigo."""
    return get_portal_article(article_id)


@router.post("", response_model=ArticleDetailResponse, status_code=status.HTTP_201_CREATED)
def create_article_route(payload: ArticleCreateRequest) -> ArticleDetailResponse:
    """Cria um artigo."""
    return create_portal_article(payload)


@router.put("/{article_id}", response_model=ArticleDetailResponse)
def update_article_route(article_id: int, payload: ArticleUpdateRequest) -> ArticleDetailResponse:
    """Atualiza um artigo existente."""
    return update_portal_article(article_id, payload)


@router.delete("/{article_id}", response_model=dict[str, str])
def delete_article_route(article_id: int) -> dict[str, str]:
    """Remove um artigo existente."""
    return delete_portal_article(article_id)
