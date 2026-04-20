"""Servico de tags."""

from backend.tags.tag_repository import TagRepository
from backend.tags.tag_schema import TagResponse


repository = TagRepository()


def list_tags(limit: int, offset: int) -> list[TagResponse]:
    """Lista tags editoriais."""
    tags = repository.list_all(limit=limit, offset=offset)
    return [
        TagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
        )
        for tag in tags
    ]
