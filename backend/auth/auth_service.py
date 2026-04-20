"""Servico de autenticacao do portal."""

from fastapi import HTTPException, status

from backend.auth.auth_repository import AuthRepository
from backend.auth.auth_schema import AuthStatusResponse, LoginRequest, TokenResponse
from backend.auth.security import (
    AUTH_NOT_IMPLEMENTED_MESSAGE,
    hash_password,
    verify_password,
    create_access_token,
)


_auth_repository = AuthRepository()


def describe_auth_module() -> AuthStatusResponse:
    """Explica o estado atual do modulo de autenticacao."""
    return AuthStatusResponse(
        provider="fastapi_custom",
        built_in_auth=False,
        note=AUTH_NOT_IMPLEMENTED_MESSAGE,
    )


def login(payload: LoginRequest) -> TokenResponse:
    """Autentica usuario e retorna JWT token."""
    user = _auth_repository.get_active_user(payload.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )
    
    # Verifica se a senha esta correta
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )
    
    # Gera token JWT
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


def register(email: str, name: str, password: str) -> dict:
    """Registra um novo usuario no sistema."""
    existing_user = _auth_repository.find_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{email}' ja cadastrado.",
        )
    
    password_hash = hash_password(password)
    user = _auth_repository.create(
        name=name,
        email=email,
        password_hash=password_hash,
        role="cliente",
    )
    
    return {
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }
