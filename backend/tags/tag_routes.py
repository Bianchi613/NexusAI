"""Rotas de tags."""

from fastapi import APIRouter, Query, status

from backend.tags.tag_controller import (
    create_editorial_tag,
    delete_editorial_tag,
    get_editorial_tag,
    list_editorial_tags,
    update_editorial_tag,
)
from backend.tags.tag_schema import TagCreateRequest, TagResponse, TagUpdateRequest


router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=list[TagResponse])
def list_tags_route(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[TagResponse]:
    """Lista tags editoriais."""
    return list_editorial_tags(limit=limit, offset=offset)


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag_route(tag_id: int) -> TagResponse:
    """Busca uma tag por id."""
    return get_editorial_tag(tag_id)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag_route(payload: TagCreateRequest) -> TagResponse:
    """Cria uma tag nova."""
    return create_editorial_tag(payload)


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag_route(tag_id: int, payload: TagUpdateRequest) -> TagResponse:
    """Atualiza uma tag existente."""
    return update_editorial_tag(tag_id, payload)


@router.delete("/{tag_id}", response_model=dict[str, str])
def delete_tag_route(tag_id: int) -> dict[str, str]:
    """Remove uma tag existente."""
    return delete_editorial_tag(tag_id)
