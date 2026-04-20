"""Controller de categorias."""

from backend.categories.category_schema import CategoryResponse
from backend.categories.category_service import list_categories


def list_editorial_categories() -> list[CategoryResponse]:
    """Lista categorias para a camada HTTP."""
    return list_categories()

