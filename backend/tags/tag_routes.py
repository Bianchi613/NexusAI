"""Rotas de tags."""

from fastapi import APIRouter, Query

from backend.tags.tag_controller import list_editorial_tags
from backend.tags.tag_schema import TagResponse


router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=list[TagResponse])
def list_tags_route(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[TagResponse]:
    """Lista tags editoriais."""
    return list_editorial_tags(limit=limit, offset=offset)

