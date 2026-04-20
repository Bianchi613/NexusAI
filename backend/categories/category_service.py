"""Servico de categorias."""

from backend.categories.category_repository import CategoryRepository
from backend.categories.category_schema import CategoryResponse


repository = CategoryRepository()


def list_categories() -> list[CategoryResponse]:
    """Lista categorias editoriais."""
    categories = repository.list_all()
    return [
        CategoryResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
        )
        for category in categories
    ]
