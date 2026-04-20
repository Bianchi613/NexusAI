"""Schemas de categorias."""

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    """Payload de criacao de categoria."""

    name: str = Field(min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120)


class CategoryUpdateRequest(BaseModel):
    """Payload de atualizacao parcial de categoria."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120)


class CategoryResponse(BaseModel):
    """Representacao publica de categoria."""

    id: int
    name: str
    slug: str
