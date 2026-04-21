"""Rotas de categorias."""

from fastapi import APIRouter, Query, status

from backend.articles.article_read_schema import ArticleReadListResponse
from backend.categories.category_controller import (
    create_editorial_category,
    delete_editorial_category,
    get_editorial_category,
    update_editorial_category,
)
from backend.categories.category_read_controller import (
    get_read_category_controller,
    list_read_categories_controller,
    list_read_category_articles_controller,
)
from backend.categories.category_read_schema import CategoryReadDetailResponse, CategoryReadSummary
from backend.categories.category_schema import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryReadSummary])
def list_categories_route(
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[CategoryReadSummary]:
    """Lista categorias visiveis para o frontend."""
    del limit, offset
    return list_read_categories_controller()


@router.get("/{category_slug}/articles", response_model=ArticleReadListResponse)
def list_category_articles_route(
    category_slug: str,
    limit: int = Query(default=12, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
) -> ArticleReadListResponse:
    """Lista artigos publicados de uma categoria."""
    return list_read_category_articles_controller(category_slug, limit=limit, offset=offset)


@router.get("/{category_slug}", response_model=CategoryReadDetailResponse)
def get_category_read_route(
    category_slug: str,
    limit: int = Query(default=12, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
) -> CategoryReadDetailResponse:
    """Retorna detalhe editorial de uma categoria pelo slug."""
    return get_read_category_controller(category_slug, limit=limit, offset=offset)


@router.get("/id/{category_id}", response_model=CategoryResponse)
def get_category_route(category_id: int) -> CategoryResponse:
    """Busca uma categoria administrativa por id."""
    return get_editorial_category(category_id)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_route(payload: CategoryCreateRequest) -> CategoryResponse:
    """Cria uma categoria nova."""
    return create_editorial_category(payload)


@router.put("/id/{category_id}", response_model=CategoryResponse)
def update_category_route(category_id: int, payload: CategoryUpdateRequest) -> CategoryResponse:
    """Atualiza uma categoria existente."""
    return update_editorial_category(category_id, payload)


@router.delete("/id/{category_id}", response_model=dict[str, str])
def delete_category_route(category_id: int) -> dict[str, str]:
    """Remove uma categoria existente."""
    return delete_editorial_category(category_id)
