"""Schemas de autenticacao."""

from pydantic import BaseModel


class AuthStatusResponse(BaseModel):
    """Explica o estado da camada de autenticacao."""

    provider: str
    built_in_auth: bool
    note: str


class LoginRequest(BaseModel):
    """Payload basico para login."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """Estrutura esperada para retorno futuro de login."""

    access_token: str
    token_type: str
