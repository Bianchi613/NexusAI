"""Servico de tags."""

from Engine.app.core.article_filters import normalize_label, slugify
from backend.tags.tag_repository import TagRepository
from backend.tags.tag_schema import TagCreateRequest, TagResponse, TagUpdateRequest


repository = TagRepository()


def _to_response(tag) -> TagResponse:
    """Converte entidade ORM para schema de resposta."""
    return TagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
    )


def _normalize_name_and_slug(*, name: str, slug: str | None) -> tuple[str, str]:
    """Normaliza o par nome/slug usado pela tag."""
    normalized_name = normalize_label(name)
    normalized_slug = slugify(slug or normalized_name)
    if not normalized_name:
        raise ValueError("Nome de tag invalido.")
    return normalized_name, normalized_slug


def list_tags(limit: int, offset: int) -> list[TagResponse]:
    """Lista tags editoriais."""
    tags = repository.list_all(limit=limit, offset=offset)
    return [_to_response(tag) for tag in tags]


def get_tag(tag_id: int) -> TagResponse | None:
    """Busca uma tag por id."""
    tag = repository.get_by_id(tag_id)
    if tag is None:
        return None
    return _to_response(tag)


def create_tag(payload: TagCreateRequest) -> TagResponse:
    """Cria uma tag nova."""
    name, slug = _normalize_name_and_slug(name=payload.name, slug=payload.slug)

    if repository.find_by_name(name) is not None:
        raise ValueError("Ja existe uma tag com este nome.")
    if repository.find_by_slug(slug) is not None:
        raise ValueError("Ja existe uma tag com este slug.")

    tag = repository.create(name=name, slug=slug)
    return _to_response(tag)


def update_tag(tag_id: int, payload: TagUpdateRequest) -> TagResponse:
    """Atualiza uma tag existente."""
    current_tag = repository.get_by_id(tag_id)
    if current_tag is None:
        raise LookupError("Tag nao encontrada.")

    name = current_tag.name
    slug = current_tag.slug

    if payload.name is not None or payload.slug is not None:
        name, slug = _normalize_name_and_slug(
            name=payload.name or current_tag.name,
            slug=payload.slug or slug,
        )

    existing_by_name = repository.find_by_name(name)
    if existing_by_name is not None and existing_by_name.id != tag_id:
        raise ValueError("Ja existe uma tag com este nome.")

    existing_by_slug = repository.find_by_slug(slug)
    if existing_by_slug is not None and existing_by_slug.id != tag_id:
        raise ValueError("Ja existe uma tag com este slug.")

    tag = repository.update(tag_id=tag_id, name=name, slug=slug)
    if tag is None:
        raise LookupError("Tag nao encontrada.")
    return _to_response(tag)


def delete_tag(tag_id: int) -> None:
    """Remove uma tag existente."""
    deleted = repository.delete(tag_id)
    if not deleted:
        raise LookupError("Tag nao encontrada.")
