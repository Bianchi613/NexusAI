"""Controller de tags."""

from fastapi import HTTPException, status

from backend.tags.tag_schema import TagCreateRequest, TagResponse, TagUpdateRequest
from backend.tags.tag_service import create_tag, delete_tag, get_tag, list_tags, update_tag


def list_editorial_tags(limit: int, offset: int) -> list[TagResponse]:
    """Lista tags para a camada HTTP."""
    return list_tags(limit=limit, offset=offset)


def get_editorial_tag(tag_id: int) -> TagResponse:
    """Retorna uma tag ou 404."""
    tag = get_tag(tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag nao encontrada.",
        )
    return tag


def create_editorial_tag(payload: TagCreateRequest) -> TagResponse:
    """Cria uma tag nova."""
    try:
        return create_tag(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


def update_editorial_tag(tag_id: int, payload: TagUpdateRequest) -> TagResponse:
    """Atualiza uma tag existente."""
    try:
        return update_tag(tag_id, payload)
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


def delete_editorial_tag(tag_id: int) -> dict[str, str]:
    """Remove uma tag existente."""
    try:
        delete_tag(tag_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return {"detail": "Tag removida com sucesso."}
