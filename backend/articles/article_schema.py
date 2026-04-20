"""Schemas de artigos."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


ArticleStatus = Literal["nao_revisada", "publicada", "rejeitada"]


class ArticleListItem(BaseModel):
    """Item resumido de artigo para listagens."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Título da matéria gerada",
                "summary": "Resumo curto da matéria gerada pelo pipeline.",
                "status": "nao_revisada",
                "category_id": 1,
                "category": "Tecnologia",
                "created_at": "2026-04-20T10:00:00-03:00",
                "reviewed_at": None,
                "published_at": None,
                "reviewed_by": None,
                "image_urls": [
                    "https://example.com/images/materia-1.jpg"
                ],
                "tag_ids": [1, 2, 3]
            }
        }
    )

    id: int = Field(example=1)
    title: str = Field(example="Título da matéria gerada")
    summary: str | None = Field(
        default=None,
        example="Resumo curto da matéria gerada pelo pipeline."
    )
    status: ArticleStatus = Field(example="nao_revisada")
    category_id: int | None = Field(default=None, example=1)
    category: str | None = Field(default=None, example="Tecnologia")
    created_at: datetime = Field(example="2026-04-20T10:00:00-03:00")
    reviewed_at: datetime | None = Field(default=None, example=None)
    published_at: datetime | None = Field(default=None, example=None)
    reviewed_by: int | None = Field(default=None, example=None)
    image_urls: list[str] = Field(
        default_factory=list,
        example=["https://example.com/images/materia-1.jpg"]
    )
    tag_ids: list[int] = Field(default_factory=list, example=[1, 2, 3])


class ArticleDetailResponse(BaseModel):
    """Resposta detalhada de artigo."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Título da matéria gerada",
                "summary": "Resumo curto da matéria gerada pelo pipeline.",
                "body": "Texto completo da matéria consolidada a partir das fontes coletadas e processadas pelo sistema.",
                "status": "nao_revisada",
                "category_id": 1,
                "category": "Tecnologia",
                "ai_model": "llama3",
                "prompt_version": "article_v1",
                "created_at": "2026-04-20T10:00:00-03:00",
                "reviewed_at": None,
                "published_at": None,
                "reviewed_by": None,
                "image_urls": [
                    "https://example.com/images/materia-1.jpg"
                ],
                "video_urls": [
                    "https://example.com/videos/materia-1.mp4"
                ],
                "tag_ids": [1, 2, 3],
                "source_ids": [10, 11]
            }
        }
    )

    id: int = Field(example=1)
    title: str = Field(example="Título da matéria gerada")
    summary: str | None = Field(
        default=None,
        example="Resumo curto da matéria gerada pelo pipeline."
    )
    body: str = Field(
        example="Texto completo da matéria consolidada a partir das fontes coletadas e processadas pelo sistema."
    )
    status: ArticleStatus = Field(example="nao_revisada")
    category_id: int | None = Field(default=None, example=1)
    category: str | None = Field(default=None, example="Tecnologia")
    ai_model: str | None = Field(default=None, example="llama3")
    prompt_version: str | None = Field(default=None, example="article_v1")
    created_at: datetime = Field(example="2026-04-20T10:00:00-03:00")
    reviewed_at: datetime | None = Field(default=None, example=None)
    published_at: datetime | None = Field(default=None, example=None)
    reviewed_by: int | None = Field(default=None, example=None)
    image_urls: list[str] = Field(
        default_factory=list,
        example=["https://example.com/images/materia-1.jpg"]
    )
    video_urls: list[str] = Field(
        default_factory=list,
        example=["https://example.com/videos/materia-1.mp4"]
    )
    tag_ids: list[int] = Field(default_factory=list, example=[1, 2, 3])
    source_ids: list[int] = Field(default_factory=list, example=[10, 11])


class ArticleCreateRequest(BaseModel):
    """Payload de criacao de artigo."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Título da matéria gerada",
                "summary": "Resumo curto da matéria gerada pelo pipeline.",
                "body": "Texto completo da matéria consolidada a partir das fontes coletadas e processadas pelo sistema.",
                "category_id": 1,
                "status": "nao_revisada",
                "ai_model": "llama3",
                "prompt_version": "article_v1",
                "tag_ids": [1, 2, 3],
                "image_urls": [
                    "https://example.com/images/materia-1.jpg"
                ],
                "video_urls": [
                    "https://example.com/videos/materia-1.mp4"
                ],
                "source_ids": [10, 11],
                "reviewed_by": None
            }
        }
    )

    title: str = Field(min_length=1, example="Título da matéria gerada")
    summary: str | None = Field(
        default=None,
        example="Resumo curto da matéria gerada pelo pipeline."
    )
    body: str = Field(
        min_length=1,
        example="Texto completo da matéria consolidada a partir das fontes coletadas e processadas pelo sistema."
    )
    category_id: int | None = Field(default=None, example=1)
    status: ArticleStatus = Field(default="nao_revisada", example="nao_revisada")
    ai_model: str | None = Field(default=None, max_length=100, example="llama3")
    prompt_version: str | None = Field(default=None, max_length=50, example="article_v1")
    tag_ids: list[int] = Field(default_factory=list, example=[1, 2, 3])
    image_urls: list[str] = Field(
        default_factory=list,
        example=["https://example.com/images/materia-1.jpg"]
    )
    video_urls: list[str] = Field(
        default_factory=list,
        example=["https://example.com/videos/materia-1.mp4"]
    )
    source_ids: list[int] = Field(default_factory=list, example=[10, 11])
    reviewed_by: int | None = Field(default=None, example=None)


class ArticleUpdateRequest(BaseModel):
    """Payload de atualizacao parcial de artigo."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Título atualizado da matéria",
                "summary": "Resumo atualizado da matéria.",
                "body": "Texto atualizado da matéria consolidada.",
                "category_id": 2,
                "status": "publicada",
                "ai_model": "llama3",
                "prompt_version": "article_v2",
                "tag_ids": [2, 4],
                "image_urls": [
                    "https://example.com/images/materia-atualizada.jpg"
                ],
                "video_urls": [
                    "https://example.com/videos/materia-atualizada.mp4"
                ],
                "source_ids": [12, 13],
                "reviewed_by": 5
            }
        }
    )

    title: str | None = Field(default=None, min_length=1, example="Título atualizado da matéria")
    summary: str | None = Field(default=None, example="Resumo atualizado da matéria.")
    body: str | None = Field(default=None, min_length=1, example="Texto atualizado da matéria consolidada.")
    category_id: int | None = Field(default=None, example=2)
    status: ArticleStatus | None = Field(default=None, example="publicada")
    ai_model: str | None = Field(default=None, max_length=100, example="llama3")
    prompt_version: str | None = Field(default=None, max_length=50, example="article_v2")
    tag_ids: list[int] | None = Field(default=None, example=[2, 4])
    image_urls: list[str] | None = Field(
        default=None,
        example=["https://example.com/images/materia-atualizada.jpg"]
    )
    video_urls: list[str] | None = Field(
        default=None,
        example=["https://example.com/videos/materia-atualizada.mp4"]
    )
    source_ids: list[int] | None = Field(default=None, example=[12, 13])
    reviewed_by: int | None = Field(default=None, example=5)