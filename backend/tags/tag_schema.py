"""Schemas de tags."""

from pydantic import BaseModel, Field


class TagCreateRequest(BaseModel):
    """Payload de criacao de tag."""

    name: str = Field(min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120)


class TagUpdateRequest(BaseModel):
    """Payload de atualizacao parcial de tag."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120)


class TagResponse(BaseModel):
    """Representacao publica de tag."""

    id: int
    name: str
    slug: str
