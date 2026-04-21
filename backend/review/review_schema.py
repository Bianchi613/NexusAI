"""Schemas de revisao editorial."""

from datetime import datetime

from pydantic import BaseModel

from backend.articles.article_schema import (
    ArticleCreateRequest,
    ArticleDetailResponse,
    ArticleListItem,
    ArticleUpdateRequest,
)
from backend.categories.category_schema import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest
from backend.tags.tag_schema import TagCreateRequest, TagResponse, TagUpdateRequest


class ReviewPendingArticle(BaseModel):
    """Item de artigo pendente de revisao."""

    id: int
    title: str
    summary: str | None = None
    status: str
    created_at: datetime
    category: str | None = None


class ReviewActionRequest(BaseModel):
    """Payload minimo para aprovar ou rejeitar."""

    reviewer_id: int


class ReviewActionResponse(BaseModel):
    """Resposta apos uma acao editorial."""

    article_id: int
    status: str
    reviewed_by: int
    reviewed_at: datetime | None = None
    published_at: datetime | None = None


class ReviewPermissionQuery(BaseModel):
    """Payload minimo para operacoes da area de revisao."""

    reviewer_id: int


class ReviewArticleCreateRequest(ArticleCreateRequest):
    """Payload de criacao de artigo pela area de revisao."""


class ReviewArticleUpdateRequest(ArticleUpdateRequest):
    """Payload de atualizacao de artigo pela area de revisao."""


class ReviewCategoryCreateRequest(CategoryCreateRequest):
    """Payload de criacao de categoria pela area de revisao."""


class ReviewCategoryUpdateRequest(CategoryUpdateRequest):
    """Payload de atualizacao de categoria pela area de revisao."""


class ReviewTagCreateRequest(TagCreateRequest):
    """Payload de criacao de tag pela area de revisao."""


class ReviewTagUpdateRequest(TagUpdateRequest):
    """Payload de atualizacao de tag pela area de revisao."""


ReviewArticleListItem = ArticleListItem
ReviewArticleDetailResponse = ArticleDetailResponse
ReviewCategoryDetailResponse = CategoryResponse
ReviewTagDetailResponse = TagResponse
