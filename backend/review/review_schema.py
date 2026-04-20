"""Schemas de revisao editorial."""

from datetime import datetime

from pydantic import BaseModel


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

