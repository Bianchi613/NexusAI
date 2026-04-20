"""Controller de categorias."""

from fastapi import HTTPException, status

from backend.categories.category_schema import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)
from backend.categories.category_service import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)


def list_editorial_categories(limit: int, offset: int) -> list[CategoryResponse]:
    """Lista categorias para a camada HTTP."""
    return list_categories(limit=limit, offset=offset)


def get_editorial_category(category_id: int) -> CategoryResponse:
    """Retorna uma categoria ou 404."""
    category = get_category(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada.",
        )
    return category


def create_editorial_category(payload: CategoryCreateRequest) -> CategoryResponse:
    """Cria uma categoria nova."""
    try:
        return create_category(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


def update_editorial_category(category_id: int, payload: CategoryUpdateRequest) -> CategoryResponse:
    """Atualiza uma categoria existente."""
    try:
        return update_category(category_id, payload)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


def delete_editorial_category(category_id: int) -> dict[str, str]:
    """Remove uma categoria existente."""
    try:
        delete_category(category_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return {"detail": "Categoria removida com sucesso."}
