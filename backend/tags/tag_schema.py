"""Schemas de tags."""

from pydantic import BaseModel


class TagResponse(BaseModel):
    """Representacao publica de tag."""

    id: int
    name: str
    slug: str

