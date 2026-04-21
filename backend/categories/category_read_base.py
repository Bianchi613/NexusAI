"""Schemas base de leitura de categorias."""

from pydantic import BaseModel


class CategoryReadSummary(BaseModel):
    """Resumo de categoria apresentado no frontend."""

    id: int
    name: str
    slug: str
    title: str
    description: str
