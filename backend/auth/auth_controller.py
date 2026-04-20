"""Controller das rotas de autenticacao."""

from backend.auth.auth_schema import AuthStatusResponse, LoginRequest, TokenResponse, RegisterRequest
from backend.auth.auth_service import describe_auth_module, login, register


def get_auth_status() -> AuthStatusResponse:
    """Explica o estado atual da autenticacao do portal."""
    return describe_auth_module()


def login_user(payload: LoginRequest) -> TokenResponse:
    """Encaminha o login para a camada de servico."""
    return login(payload)


def register_user(payload: RegisterRequest) -> dict:
    """Encaminha o registro de novo usuario para a camada de servico."""
    return register(
        email=payload.email,
        name=payload.name,
        password=payload.password,
    )
