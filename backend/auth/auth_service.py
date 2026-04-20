"""Servico de autenticacao do portal."""

from fastapi import HTTPException, status

from backend.auth.auth_schema import AuthStatusResponse, LoginRequest, TokenResponse
from backend.auth.security import AUTH_NOT_IMPLEMENTED_MESSAGE


def describe_auth_module() -> AuthStatusResponse:
    """Explica o estado atual do modulo de autenticacao."""
    return AuthStatusResponse(
        provider="fastapi_custom",
        built_in_auth=False,
        note=AUTH_NOT_IMPLEMENTED_MESSAGE,
    )


def login(payload: LoginRequest) -> TokenResponse:
    """Scaffold do login.

    A rota existe para marcar o fluxo na arquitetura, mas a implementacao
    real de senha, token e permissoes vem na proxima etapa.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            f"Login ainda nao implementado para '{payload.email}'. "
            f"{AUTH_NOT_IMPLEMENTED_MESSAGE}"
        ),
    )
