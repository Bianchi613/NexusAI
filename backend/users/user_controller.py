"""Controller de usuarios."""

from fastapi import HTTPException, status

from backend.users.user_schema import UserResponse
from backend.users.user_service import get_user, list_users


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

