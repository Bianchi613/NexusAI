"""Rotas de usuarios."""

from fastapi import APIRouter, Query

from backend.users.user_controller import get_portal_user, list_portal_users
from backend.users.user_schema import UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
def list_users_route(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[UserResponse]:
    """Lista usuarios cadastrados."""
    return list_portal_users(limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_route(user_id: int) -> UserResponse:
    """Retorna um usuario por id."""
    return get_portal_user(user_id)

