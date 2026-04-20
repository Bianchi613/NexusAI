"""Rotas de revisao editorial."""

from fastapi import APIRouter, Query

from backend.review.review_controller import (
    approve_review_article,
    list_pending_review_articles,
    reject_review_article,
)
from backend.review.review_schema import ReviewActionRequest, ReviewActionResponse, ReviewPendingArticle


router = APIRouter(prefix="/review", tags=["Review"])


@router.get("/articles/pending", response_model=list[ReviewPendingArticle])
def list_pending_articles_route(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ReviewPendingArticle]:
    """Lista artigos pendentes de revisao."""
    return list_pending_review_articles(limit=limit, offset=offset)


@router.patch("/articles/{article_id}/approve", response_model=ReviewActionResponse)
def approve_article_route(article_id: int, payload: ReviewActionRequest) -> ReviewActionResponse:
    """Aprova e publica um artigo."""
    return approve_review_article(article_id=article_id, reviewer_id=payload.reviewer_id)


@router.patch("/articles/{article_id}/reject", response_model=ReviewActionResponse)
def reject_article_route(article_id: int, payload: ReviewActionRequest) -> ReviewActionResponse:
    """Rejeita um artigo pendente."""
    return reject_review_article(article_id=article_id, reviewer_id=payload.reviewer_id)

