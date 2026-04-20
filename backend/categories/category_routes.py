"""Rotas de categorias."""

from fastapi import APIRouter

from backend.categories.category_controller import list_editorial_categories
from backend.categories.category_schema import CategoryResponse


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories_route() -> list[CategoryResponse]:
    """Lista categorias editoriais."""
    return list_editorial_categories()

