"""Servico de categorias."""

from app.core.article_filters import normalize_label, slugify
from backend.categories.category_repository import CategoryRepository
from backend.categories.category_schema import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest


repository = CategoryRepository()


def _to_response(category) -> CategoryResponse:
    """Converte entidade ORM para schema de resposta."""
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
    )


def _normalize_name_and_slug(*, name: str, slug: str | None) -> tuple[str, str]:
    """Normaliza o par nome/slug usado pela categoria."""
    normalized_name = normalize_label(name)
    normalized_slug = slugify(slug or normalized_name)
    if not normalized_name:
        raise ValueError("Nome de categoria invalido.")
    return normalized_name, normalized_slug


def list_categories(limit: int, offset: int) -> list[CategoryResponse]:
    """Lista categorias editoriais."""
    categories = repository.list_all(limit=limit, offset=offset)
    return [_to_response(category) for category in categories]


def get_category(category_id: int) -> CategoryResponse | None:
    """Busca uma categoria por id."""
    category = repository.get_by_id(category_id)
    if category is None:
        return None
    return _to_response(category)


def create_category(payload: CategoryCreateRequest) -> CategoryResponse:
    """Cria uma categoria nova."""
    name, slug = _normalize_name_and_slug(name=payload.name, slug=payload.slug)

    if repository.find_by_name(name) is not None:
        raise ValueError("Ja existe uma categoria com este nome.")
    if repository.find_by_slug(slug) is not None:
        raise ValueError("Ja existe uma categoria com este slug.")

    category = repository.create(name=name, slug=slug)
    return _to_response(category)


def update_category(category_id: int, payload: CategoryUpdateRequest) -> CategoryResponse:
    """Atualiza uma categoria existente."""
    current_category = repository.get_by_id(category_id)
    if current_category is None:
        raise LookupError("Categoria nao encontrada.")

    name = current_category.name
    slug = current_category.slug

    if payload.name is not None or payload.slug is not None:
        name, slug = _normalize_name_and_slug(
            name=payload.name or current_category.name,
            slug=payload.slug or slug,
        )

    existing_by_name = repository.find_by_name(name)
    if existing_by_name is not None and existing_by_name.id != category_id:
        raise ValueError("Ja existe uma categoria com este nome.")

    existing_by_slug = repository.find_by_slug(slug)
    if existing_by_slug is not None and existing_by_slug.id != category_id:
        raise ValueError("Ja existe uma categoria com este slug.")

    category = repository.update(category_id=category_id, name=name, slug=slug)
    if category is None:
        raise LookupError("Categoria nao encontrada.")
    return _to_response(category)


def delete_category(category_id: int) -> None:
    """Remove uma categoria existente."""
    deleted = repository.delete(category_id)
    if not deleted:
        raise LookupError("Categoria nao encontrada.")
