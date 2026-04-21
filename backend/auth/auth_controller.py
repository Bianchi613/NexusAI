"""Controller das rotas de autenticacao."""

from backend.auth.auth_schema import (
    AuthStatusResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
)
from backend.auth.auth_service import describe_auth_module, login, register, request_password_reset, reset_password


def get_auth_status() -> AuthStatusResponse:
    """Explica o estado atual da autenticacao do portal."""
    return describe_auth_module()


def login_user(payload: LoginRequest) -> TokenResponse:
    """Encaminha o login para a camada de servico."""
    return login(payload)


def register_user(payload: RegisterRequest) -> RegisterResponse:
    """Encaminha o registro de novo usuario para a camada de servico."""
    return register(
        email=payload.email,
        name=payload.name,
        password=payload.password,
    )


def forgot_password_user(payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
    """Encaminha a solicitacao de redefinicao de senha."""
    return request_password_reset(payload.email)


def reset_password_user(payload: ResetPasswordRequest) -> ResetPasswordResponse:
    """Encaminha a redefinicao de senha."""
    return reset_password(token=payload.token, new_password=payload.new_password)
