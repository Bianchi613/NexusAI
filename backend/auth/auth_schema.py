"""Schemas de autenticacao."""

from pydantic import BaseModel, EmailStr, Field


class AuthStatusResponse(BaseModel):
    """Explica o estado da camada de autenticacao."""

    provider: str = Field(examples=["fastapi_custom"])
    built_in_auth: bool = Field(examples=[False])
    note: str = Field(examples=["A arquitetura de auth ja foi separada..."])


class LoginRequest(BaseModel):
    """Payload basico para login."""

    email: str = Field(examples=["alan.silva@example.com"])
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
