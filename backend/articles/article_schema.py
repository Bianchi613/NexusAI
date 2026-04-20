"""Schemas publicos de artigos."""

from datetime import datetime

from pydantic import BaseModel, Field


class ArticleListItem(BaseModel):
    """Item resumido de artigo para listagens."""

    id: int
    title: str
    summary: str | None = None
    category: str | None = None
    published_at: datetime | None = None
    image_urls: list[str] = Field(default_factory=list)


class ArticleDetailResponse(BaseModel):
    """Resposta detalhada de artigo publico."""

    id: int
    title: str
    summary: str | None = None
    body: str
    category: str | None = None
    published_at: datetime | None = None
    image_urls: list[str] = Field(default_factory=list)
    video_urls: list[str] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)
