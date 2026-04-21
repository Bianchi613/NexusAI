"""Rotas relacionadas a autenticacao."""

from fastapi import APIRouter, Response, Security, status

from backend.auth.auth_controller import forgot_password_user, login_user, register_user, reset_password_user
from backend.auth.auth_schema import (
    AuthStatusProtectedResponse,
    AuthStatusResponse,
    CurrentUserResponse,
    ErrorResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
)
from backend.auth.auth_service import build_auth_runtime_status
from backend.auth.security import get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])

AUTH_STATUS_READY_EXAMPLE = {
    "status": "ready",
    "ready": True,
    "provider": "fastapi_custom",
    "built_in_auth": False,
    "checks": {
        "jwt_secret_configured": True,
        "jwt_secret_not_default": True,
        "jwt_secret_min_length": True,
        "access_token_expiration_valid": True,
    },
    "note": "Auth pronto para operacao basica com bcrypt e JWT.",
}

AUTH_STATUS_DEGRADED_EXAMPLE = {
    "status": "degraded",
    "ready": False,
    "provider": "fastapi_custom",
    "built_in_auth": False,
    "checks": {
        "jwt_secret_configured": True,
        "jwt_secret_not_default": False,
        "jwt_secret_min_length": True,
        "access_token_expiration_valid": True,
    },
    "note": (
        "Auth funcional em desenvolvimento, mas degradado para operacao: "
        "configure JWT_SECRET_KEY forte e mantenha expiracao valida."
    ),
}

AUTH_STATUS_PROTECTED_DEGRADED_EXAMPLE = {
    **AUTH_STATUS_DEGRADED_EXAMPLE,
    "authenticated_user": "alan.silva@example.com",
}

CURRENT_USER_EXAMPLE = {
    "user_id": 1,
    "email": "alan.silva@example.com",
    "role": "cliente",
}

TOKEN_RESPONSE_EXAMPLE = {
    "access_token": (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxIiwgImVtYWlsIjoiYWxhbi5zaWx2YUBleGFtcGxlLmNvbSIs"
        "ICJyb2xlIjoiY2xpZW50ZSIsImV4cCI6MTYxNjIzOTAyMn0.signature"
    ),
    "token_type": "bearer",
}

REGISTER_RESPONSE_EXAMPLE = {
    "user_id": 1,
    "email": "alan.silva@example.com",
    "name": "Alan Silva",
    "role": "cliente",
}

FORGOT_PASSWORD_RESPONSE_EXAMPLE = {
    "message": "Solicitacao recebida. Neste ambiente, o token de redefinicao e retornado diretamente para concluir o fluxo no frontend.",
    "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.reset-password.signature",
    "expires_in_minutes": 30,
}

RESET_PASSWORD_RESPONSE_EXAMPLE = {
    "message": "Senha redefinida com sucesso.",
}

ERROR_TOKEN_MISSING_EXAMPLE = {"detail": "Token nao fornecido."}
ERROR_TOKEN_INVALID_EXAMPLE = {"detail": "Token invalido ou expirado."}
ERROR_INVALID_CREDENTIALS_EXAMPLE = {"detail": "Credenciais invalidas."}
ERROR_EMAIL_EXISTS_EXAMPLE = {"detail": "Email 'alan.silva@example.com' ja cadastrado."}


@router.get(
    "/status",
    response_model=AuthStatusResponse,
    responses={
        200: {
            "description": "Autenticacao pronta para operacao basica",
            "content": {
                "application/json": {
                    "example": AUTH_STATUS_READY_EXAMPLE,
                }
            },
        },
        503: {
            "description": "Autenticacao degradada ou mal configurada",
            "model": AuthStatusResponse,
            "content": {
                "application/json": {
                    "example": AUTH_STATUS_DEGRADED_EXAMPLE,
                }
            },
        },
    },
)
def auth_status_public(response: Response) -> AuthStatusResponse:
    """Explica o estado operacional atual do modulo de autenticacao (publico)."""
    runtime_status = build_auth_runtime_status()
    response.status_code = runtime_status.http_status
    return runtime_status.response


@router.get(
    "/status/protected",
    response_model=AuthStatusProtectedResponse,
    responses={
        200: {
            "description": "Autenticacao validada com token Bearer",
            "content": {
                "application/json": {
                    "example": AUTH_STATUS_PROTECTED_DEGRADED_EXAMPLE,
                }
            },
        },
        401: {
            "description": "Token invalido ou nao fornecido",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "token_missing": {
                            "summary": "Sem token",
                            "value": ERROR_TOKEN_MISSING_EXAMPLE,
                        },
                        "token_invalid": {
                            "summary": "Token invalido",
                            "value": ERROR_TOKEN_INVALID_EXAMPLE,
                        },
                    }
                }
            },
        },
    }
)
async def auth_status_protected(
    current_user: dict = Security(get_current_user)
) -> AuthStatusProtectedResponse:
    """Explica o estado da autenticacao (requer token).

    **Requer autenticacao Bearer (JWT token)**

    Use esta rota para testar o Authorize no Swagger.
    """
    status_data = build_auth_runtime_status().response.model_dump()
    status_data["authenticated_user"] = current_user.get("email")
    return AuthStatusProtectedResponse(**status_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        200: {
            "description": "Login realizado com sucesso",
            "content": {
                "application/json": {
                    "example": TOKEN_RESPONSE_EXAMPLE,
                }
            },
        },
        401: {
            "description": "Credenciais invalidas",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": ERROR_INVALID_CREDENTIALS_EXAMPLE,
                }
            },
        },
    },
)
def login(payload: LoginRequest) -> TokenResponse:
    """Faz login e retorna um JWT token."""
    return login_user(payload)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Usuario registrado com sucesso",
            "content": {
                "application/json": {
                    "example": REGISTER_RESPONSE_EXAMPLE,
                }
            },
        },
        400: {
            "description": "Email ja cadastrado",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": ERROR_EMAIL_EXISTS_EXAMPLE,
                }
            },
        },
    },
)
def register(payload: RegisterRequest) -> RegisterResponse:
    """Registra um novo usuario no sistema."""
    return register_user(payload)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    responses={
        200: {
            "description": "Fluxo de redefinicao iniciado",
            "content": {
                "application/json": {
                    "example": FORGOT_PASSWORD_RESPONSE_EXAMPLE,
                }
            },
        },
    },
)
def forgot_password(payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
    """Inicia a recuperacao de senha."""
    return forgot_password_user(payload)


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    responses={
        200: {
            "description": "Senha redefinida com sucesso",
            "content": {
                "application/json": {
                    "example": RESET_PASSWORD_RESPONSE_EXAMPLE,
                }
            },
        },
        400: {
            "description": "Token invalido ou expirado",
            "model": ErrorResponse,
        },
    },
)
def reset_password(payload: ResetPasswordRequest) -> ResetPasswordResponse:
    """Conclui a redefinicao de senha."""
    return reset_password_user(payload)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    responses={
        200: {
            "description": "Usuario autenticado",
            "content": {
                "application/json": {
                    "example": CURRENT_USER_EXAMPLE,
                }
            },
        },
        401: {
            "description": "Token invalido ou nao fornecido",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "token_missing": {
                            "summary": "Sem token",
                            "value": ERROR_TOKEN_MISSING_EXAMPLE,
                        },
                        "token_invalid": {
                            "summary": "Token invalido",
                            "value": ERROR_TOKEN_INVALID_EXAMPLE,
                        },
                    }
                }
            },
        },
    }
)
async def get_user_info(
    current_user: dict = Security(get_current_user)
) -> CurrentUserResponse:
    """Retorna os dados do usuario autenticado.

    **Requer autenticacao Bearer (JWT token)**

    Passos:
    1. Faca login em POST /auth/login
    2. Copie o token retornado
    3. Clique em 'Authorize' (cadeado) no topo
    4. Cole o token (sem "Bearer", so o hash)
    5. Clique "Authorize"
    6. Chame esta rota
    """
    return CurrentUserResponse(
        user_id=int(current_user.get("sub")),
        email=current_user.get("email"),
        role=current_user.get("role"),
    )
