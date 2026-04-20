"""Rotas relacionadas a autenticacao."""

from fastapi import APIRouter

from backend.auth.auth_controller import get_auth_status, login_user
from backend.auth.auth_schema import AuthStatusResponse, LoginRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/status", response_model=AuthStatusResponse)
def auth_status() -> AuthStatusResponse:
    """Explica o estado atual do modulo de autenticacao."""
    return get_auth_status()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    """Scaffold da rota de login."""
    return login_user(payload)
