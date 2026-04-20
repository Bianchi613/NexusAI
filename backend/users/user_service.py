"""Servico de usuarios."""

from backend.users.user_repository import UserRepository
from backend.users.user_schema import UserResponse


repository = UserRepository()


def list_users(limit: int, offset: int) -> list[UserResponse]:
    """Lista usuarios cadastrados no portal."""
    users = repository.list_all(limit=limit, offset=offset)
    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        for user in users
    ]


def get_user(user_id: int) -> UserResponse | None:
    """Busca um usuario por id."""
    user = repository.get_by_id(user_id)
    if user is None:
        return None

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )
