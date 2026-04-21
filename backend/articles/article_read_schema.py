"""Schemas de leitura de artigos usados pelo frontend."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from backend.categories.category_read_base import CategoryReadSummary


class TagReadItem(BaseModel):
    """Tag publica de um artigo."""

    id: int
    name: str
    slug: str


class ArticleSourceReadItem(BaseModel):
    """Fonte original vinculada a uma materia publicada."""

    raw_article_id: int
    source_name: str | None = None
    original_title: str
    original_url: str
    original_author: str | None = None


class ArticleCardResponse(BaseModel):
    """Card resumido de artigo para listas e carrosseis."""

    id: int
    slug: str
    title: str
    summary: str | None = None
    excerpt: str | None = None
    label: str
    category: CategoryReadSummary | None = None
    author: str
    published_at: datetime | None = None
    read_time_minutes: int
    location: str | None = None
    image_url: str | None = None
    video_url: str | None = None


class ArticleReadListResponse(BaseModel):
    """Resposta paginada de artigos publicados."""

    items: list[ArticleCardResponse]
    limit: int
    offset: int
    has_more: bool


class ArticleReadDetailResponse(BaseModel):
    """Detalhe completo de um artigo publicado."""

    id: int
    slug: str
    title: str
    summary: str | None = None
    body: str
    body_paragraphs: list[str]
    label: str
    category: CategoryReadSummary | None = None
    author: str
    published_at: datetime | None = None
    read_time_minutes: int
    location: str | None = None
    image_urls: list[str]
    video_urls: list[str]
    tags: list[TagReadItem]
    source_articles: list[ArticleSourceReadItem]
    related_articles: list[ArticleCardResponse]
