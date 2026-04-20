"""Controller de usuarios."""

from fastapi import HTTPException, status

from backend.users.user_schema import UserCreateRequest, UserResponse, UserUpdateRequest
from backend.users.user_service import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)


def list_portal_users(limit: int, offset: int) -> list[UserResponse]:
    """Lista usuarios para a camada HTTP."""
    return list_users(limit=limit, offset=offset)


def get_portal_user(user_id: int) -> UserResponse:
    """Retorna um usuario ou 404."""
    user = get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado.",
        )
    return user


def create_portal_user(payload: UserCreateRequest) -> UserResponse:
    """Cria um usuario para a camada HTTP."""
    try:
        return create_user(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


def update_portal_user(user_id: int, payload: UserUpdateRequest) -> UserResponse:
    """Atualiza um usuario existente."""
    try:
        return update_user(user_id, payload)
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


def delete_portal_user(user_id: int) -> dict[str, str]:
    """Remove um usuario existente."""
    try:
        delete_user(user_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return {"detail": "Usuario removido com sucesso."}
