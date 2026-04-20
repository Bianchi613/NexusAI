"""Schemas de usuarios."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


UserRole = Literal["cliente", "revisor"]


class UserCreateRequest(BaseModel):
    """Payload de criacao de usuario."""

    name: str = Field(min_length=1, max_length=150, examples=["Alan Silva"])
    email: EmailStr = Field(examples=["alan.silva@example.com"])
    password: str = Field(min_length=6, max_length=255, examples=["Senha@123"])
    role: UserRole = Field(default="cliente", examples=["cliente"])
    is_active: bool = Field(default=True, examples=[True])

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Alan Silva",
                "email": "alan.silva@example.com",
                "password": "Senha@123",
                "role": "cliente",
                "is_active": True
            }
        }
    }


class UserUpdateRequest(BaseModel):
    """Payload de atualizacao parcial de usuario."""

    name: str | None = Field(default=None, min_length=1, max_length=150, examples=["Alan Silva"])
    email: EmailStr | None = Field(default=None, examples=["alan.silva@example.com"])
    password: str | None = Field(default=None, min_length=6, max_length=255, examples=["NovaSenha@123"])
    role: UserRole | None = Field(default=None, examples=["revisor"])
    is_active: bool | None = Field(default=None, examples=[True])

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Alan Silva",
                "email": "alan.silva@example.com",
                "password": "NovaSenha@123",
                "role": "revisor",
                "is_active": True
            }
        }
    }


class UserResponse(BaseModel):
    """Representacao simples de usuario para a API."""

    id: int = Field(examples=[1])
    name: str = Field(examples=["Alan Silva"])
    email: str = Field(examples=["alan.silva@example.com"])
    role: str = Field(examples=["cliente"])
    is_active: bool = Field(examples=[True])
    created_at: datetime = Field(examples=["2026-04-20T10:30:00"])
    updated_at: datetime = Field(examples=["2026-04-20T10:30:00"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Alan Silva",
                "email": "alan.silva@example.com",
                "role": "cliente",
                "is_active": True,
                "created_at": "2026-04-20T10:30:00",
                "updated_at": "2026-04-20T10:30:00"
            }
        }
    }