"""Controller de tags."""

from backend.tags.tag_schema import TagResponse
from backend.tags.tag_service import list_tags


def list_editorial_tags(limit: int, offset: int) -> list[TagResponse]:
    """Lista tags para a camada HTTP."""
    return list_tags(limit=limit, offset=offset)

