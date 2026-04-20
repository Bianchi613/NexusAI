"""Servico de usuarios."""

from backend.auth.security import hash_password
from backend.users.user_repository import UserRepository
from backend.users.user_schema import UserCreateRequest, UserResponse, UserUpdateRequest


repository = UserRepository()


def _to_response(user) -> UserResponse:
    """Converte entidade ORM para schema de resposta."""
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def list_users(limit: int, offset: int) -> list[UserResponse]:
    """Lista usuarios cadastrados no portal."""
    users = repository.list_all(limit=limit, offset=offset)
    return [_to_response(user) for user in users]


def get_user(user_id: int) -> UserResponse | None:
    """Busca um usuario por id."""
    user = repository.get_by_id(user_id)
    if user is None:
        return None
    return _to_response(user)


def create_user(payload: UserCreateRequest) -> UserResponse:
    """Cria um usuario novo."""
    normalized_email = payload.email.strip().lower()
    if repository.find_by_email(normalized_email) is not None:
        raise ValueError("Ja existe um usuario com este email.")

    user = repository.create(
        name=payload.name.strip(),
        email=normalized_email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    return _to_response(user)


def update_user(user_id: int, payload: UserUpdateRequest) -> UserResponse:
    """Atualiza um usuario existente."""
    current_user = repository.get_by_id(user_id)
    if current_user is None:
        raise LookupError("Usuario nao encontrado.")

    updates: dict[str, object] = {}

    if payload.name is not None:
        updates["name"] = payload.name.strip()

    if payload.email is not None:
        normalized_email = payload.email.strip().lower()
        existing_user = repository.find_by_email(normalized_email)
        if existing_user is not None and existing_user.id != user_id:
            raise ValueError("Ja existe um usuario com este email.")
        updates["email"] = normalized_email

    if payload.password is not None:
        updates["password_hash"] = hash_password(payload.password)

    if payload.role is not None:
        updates["role"] = payload.role

    if payload.is_active is not None:
        updates["is_active"] = payload.is_active

    updated_user = repository.update(user_id=user_id, updates=updates)
    if updated_user is None:
        raise LookupError("Usuario nao encontrado.")

    return _to_response(updated_user)


def delete_user(user_id: int) -> None:
    """Remove um usuario existente."""
    deleted = repository.delete(user_id)
    if not deleted:
        raise LookupError("Usuario nao encontrado.")
