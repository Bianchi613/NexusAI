"""Schemas de autenticacao."""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class AuthStatusResponse(BaseModel):
    """Explica o estado da camada de autenticacao."""

    status: Literal["ready", "degraded"] = Field(examples=["ready"])
    ready: bool = Field(examples=[True])
    provider: str = Field(examples=["fastapi_custom"])
    built_in_auth: bool = Field(examples=[False])
    checks: dict[str, bool] = Field(
        examples=[
            {
                "jwt_secret_configured": True,
                "jwt_secret_not_default": True,
                "jwt_secret_min_length": True,
                "access_token_expiration_valid": True,
            }
        ]
    )
    note: str = Field(
        examples=[
            "Auth pronto para operacao basica com bcrypt e JWT."
        ]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class LoginRequest(BaseModel):
    """Payload basico para login."""

    email: EmailStr = Field(examples=["alan.silva@example.com"])
    password: str = Field(examples=["Senha@123"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "alan.silva@example.com",
                "password": "Senha@123"
            }
        }
    }


class RegisterRequest(BaseModel):
    """Payload para registro de novo usuario."""

    email: EmailStr = Field(examples=["alan.silva@example.com"])
    name: str = Field(min_length=1, max_length=150, examples=["Alan Silva"])
    password: str = Field(min_length=6, max_length=255, examples=["Senha@123"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "alan.silva@example.com",
                "name": "Alan Silva",
                "password": "Senha@123"
            }
        }
    }


class ForgotPasswordRequest(BaseModel):
    """Payload para iniciar recuperacao de senha."""

    email: EmailStr = Field(examples=["alan.silva@example.com"])


class ForgotPasswordResponse(BaseModel):
    """Resposta da solicitacao de recuperacao de senha."""

    message: str = Field(examples=["Se o e-mail existir, o fluxo de redefinicao foi iniciado."])
    reset_token: str | None = Field(default=None, examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    expires_in_minutes: int | None = Field(default=None, examples=[30])


class ResetPasswordRequest(BaseModel):
    """Payload para redefinir senha a partir de token."""

    token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    new_password: str = Field(min_length=6, max_length=255, examples=["NovaSenha@123"])


class ResetPasswordResponse(BaseModel):
    """Resposta simples apos redefinicao de senha."""

    message: str = Field(examples=["Senha redefinida com sucesso."])


class TokenResponse(BaseModel):
    """Estrutura esperada para retorno futuro de login."""

    access_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field(examples=["bearer"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJlbWFpbCI6ImFsYW4uc2lsdmFAZXhhbXBsZS5jb20iLCJyb2xlIjoiY2xpZW50ZSIsImV4cCI6MTYxNjIzOTAyMn0.signature",
                "token_type": "bearer"
            }
        }
    }


class RegisterResponse(BaseModel):
    """Estrutura de resposta para criacao de usuario via auth."""

    user_id: int = Field(examples=[1])
    email: EmailStr = Field(examples=["alan.silva@example.com"])
    name: str = Field(examples=["Alan Silva"])
    role: str = Field(examples=["cliente"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "email": "alan.silva@example.com",
                "name": "Alan Silva",
                "role": "cliente"
            }
        }
    }


class AuthStatusProtectedResponse(AuthStatusResponse):
    """Status publico enriquecido com o usuario autenticado."""

    authenticated_user: EmailStr = Field(examples=["alan.silva@example.com"])


class CurrentUserResponse(BaseModel):
    """Dados basicos do usuario autenticado."""

    user_id: int = Field(examples=[1])
    email: EmailStr = Field(examples=["alan.silva@example.com"])
    role: str = Field(examples=["cliente"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "email": "alan.silva@example.com",
                "role": "cliente"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Erro simples retornado pela API."""

    detail: str = Field(examples=["Credenciais invalidas."])

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Credenciais invalidas."
            }
        }
    }
