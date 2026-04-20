"""Rotas de usuarios."""

from fastapi import APIRouter, Query, status

from backend.users.user_controller import (
    create_portal_user,
    delete_portal_user,
    get_portal_user,
    list_portal_users,
    update_portal_user,
)
from backend.users.user_schema import UserCreateRequest, UserResponse, UserUpdateRequest


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


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_route(payload: UserCreateRequest) -> UserResponse:
    """Cria um usuario."""
    return create_portal_user(payload)


@router.put("/{user_id}", response_model=UserResponse)
def update_user_route(user_id: int, payload: UserUpdateRequest) -> UserResponse:
    """Atualiza um usuario existente."""
    return update_portal_user(user_id, payload)


@router.delete("/{user_id}", response_model=dict[str, str])
def delete_user_route(user_id: int) -> dict[str, str]:
    """Remove um usuario existente."""
    return delete_portal_user(user_id)
