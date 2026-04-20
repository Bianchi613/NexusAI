"""Schemas de usuarios."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


UserRole = Literal["cliente", "revisor"]


class UserCreateRequest(BaseModel):
    """Payload de criacao de usuario."""

    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=255)
    role: UserRole = "cliente"
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    """Payload de atualizacao parcial de usuario."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    """Representacao simples de usuario para a API."""

    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
