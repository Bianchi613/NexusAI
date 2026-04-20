"""Schemas de artigos."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ArticleStatus = Literal["nao_revisada", "publicada", "rejeitada"]


class ArticleListItem(BaseModel):
    """Item resumido de artigo para listagens."""

    id: int
    title: str
    summary: str | None = None
    status: ArticleStatus
    category_id: int | None = None
    category: str | None = None
    created_at: datetime
    reviewed_at: datetime | None = None
    published_at: datetime | None = None
    reviewed_by: int | None = None
    image_urls: list[str] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)


class ArticleDetailResponse(BaseModel):
    """Resposta detalhada de artigo."""

    id: int
    title: str
    summary: str | None = None
    body: str
    status: ArticleStatus
    category_id: int | None = None
    category: str | None = None
    ai_model: str | None = None
    prompt_version: str | None = None
    created_at: datetime
    reviewed_at: datetime | None = None
    published_at: datetime | None = None
    reviewed_by: int | None = None
    image_urls: list[str] = Field(default_factory=list)
    video_urls: list[str] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)


class ArticleCreateRequest(BaseModel):
    """Payload de criacao de artigo."""

    title: str = Field(min_length=1)
    summary: str | None = None
    body: str = Field(min_length=1)
    category_id: int | None = None
    status: ArticleStatus = "nao_revisada"
    ai_model: str | None = Field(default=None, max_length=100)
    prompt_version: str | None = Field(default=None, max_length=50)
    tag_ids: list[int] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)
    video_urls: list[str] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)
    reviewed_by: int | None = None


class ArticleUpdateRequest(BaseModel):
    """Payload de atualizacao parcial de artigo."""

    title: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    body: str | None = Field(default=None, min_length=1)
    category_id: int | None = None
    status: ArticleStatus | None = None
    ai_model: str | None = Field(default=None, max_length=100)
    prompt_version: str | None = Field(default=None, max_length=50)
    tag_ids: list[int] | None = None
    image_urls: list[str] | None = None
    video_urls: list[str] | None = None
    source_ids: list[int] | None = None
    reviewed_by: int | None = None
