"""Schemas de categorias."""

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    """Representacao publica de categoria."""

    id: int
    name: str
    slug: str

