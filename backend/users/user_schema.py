"""Schemas de usuarios."""

from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Representacao simples de usuario para a API."""

    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

