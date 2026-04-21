"""Schemas de leitura de categorias usados pelo frontend."""

from __future__ import annotations

from pydantic import BaseModel

from backend.categories.category_read_base import CategoryReadSummary


class CategoryReadResponse(BaseModel):
    """Detalhe editorial de uma categoria."""

    id: int
    name: str
    slug: str
    title: str
    description: str
    rail_title: str
    rail_items: list[str]


class CategoryReadDetailResponse(BaseModel):
    """Detalhe de uma categoria com vitrine de artigos."""

    category: CategoryReadResponse
    featured_article: "ArticleCardResponse | None" = None
    articles: list["ArticleCardResponse"]
    limit: int
    offset: int
    has_more: bool


from backend.articles.article_read_schema import ArticleCardResponse

CategoryReadDetailResponse.model_rebuild()
