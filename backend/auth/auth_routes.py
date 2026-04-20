"""Rotas relacionadas a autenticacao."""

from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPBearer

from backend.auth.auth_controller import get_auth_status, login_user, register_user
from backend.auth.auth_schema import AuthStatusResponse, LoginRequest, TokenResponse, RegisterRequest
from backend.auth.security import get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()


@router.get("/status", response_model=AuthStatusResponse)
def auth_status_public() -> AuthStatusResponse:
    """Explica o estado atual do modulo de autenticacao (publico)."""
    return get_auth_status()


@router.get(
    "/status/protected",
    responses={
        401: {"description": "Token invalido ou nao fornecido"},
    }
)
async def auth_status_protected(
    current_user: dict = Security(get_current_user)
) -> dict:
    """Explica o estado da autenticacao (requer token).
    
    **Requer autenticacao Bearer (JWT token)**
    
    Use esta rota para testar o Authorize no Swagger!
    """
    status_data = get_auth_status().dict()
    status_data["authenticated_user"] = current_user.get("email")
    return status_data


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    """Faz login e retorna um JWT token."""
    return login_user(payload)


@router.post("/register")
def register(payload: RegisterRequest) -> dict:
    """Registra um novo usuario no sistema."""
    return register_user(payload)


@router.get(
    "/me",
    responses={
        401: {"description": "Token invalido ou nao fornecido"},
    }
)
async def get_user_info(
    current_user: dict = Security(get_current_user)
) -> dict:
    """Retorna os dados do usuario autenticado.
    
    **Requer autenticacao Bearer (JWT token)**
    
    Passos:
    1. Faça login em POST /auth/login
    2. Copie o token retornado
    3. Clique em 'Authorize' (cadeado) no topo
    4. Cole o token (sem "Bearer", só o hash)
    5. Clique "Authorize"
    6. Chame esta rota
    """
    return {
        "user_id": current_user.get("sub"),
        "email": current_user.get("email"),
        "role": current_user.get("role"),
    }
