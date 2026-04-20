"""Rotas de categorias."""

from fastapi import APIRouter, Query, status

from backend.categories.category_controller import (
    create_editorial_category,
    delete_editorial_category,
    get_editorial_category,
    list_editorial_categories,
    update_editorial_category,
)
from backend.categories.category_schema import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories_route(
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[CategoryResponse]:
    """Lista categorias editoriais."""
    return list_editorial_categories(limit=limit, offset=offset)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_route(category_id: int) -> CategoryResponse:
    """Busca uma categoria por id."""
    return get_editorial_category(category_id)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_route(payload: CategoryCreateRequest) -> CategoryResponse:
    """Cria uma categoria nova."""
    return create_editorial_category(payload)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category_route(category_id: int, payload: CategoryUpdateRequest) -> CategoryResponse:
    """Atualiza uma categoria existente."""
    return update_editorial_category(category_id, payload)


@router.delete("/{category_id}", response_model=dict[str, str])
def delete_category_route(category_id: int) -> dict[str, str]:
    """Remove uma categoria existente."""
    return delete_editorial_category(category_id)
