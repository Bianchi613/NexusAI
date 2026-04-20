"""Controller das rotas de autenticacao."""

from backend.auth.auth_schema import AuthStatusResponse, LoginRequest, TokenResponse
from backend.auth.auth_service import describe_auth_module, login


def get_auth_status() -> AuthStatusResponse:
    """Explica o estado atual da autenticacao do portal."""
    return describe_auth_module()


def login_user(payload: LoginRequest) -> TokenResponse:
    """Encaminha o login para a camada de servico."""
    return login(payload)
