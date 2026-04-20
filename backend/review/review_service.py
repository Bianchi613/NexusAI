"""Servico de revisao editorial."""

from fastapi import HTTPException, status

from backend.articles.article_repository import ArticleRepository
from backend.review.review_schema import ReviewActionResponse, ReviewPendingArticle
from backend.users.user_repository import UserRepository

article_repository = ArticleRepository()
user_repository = UserRepository()


def list_pending_articles(limit: int, offset: int) -> list[ReviewPendingArticle]:
    """Lista artigos que aguardam revisao."""
    articles = article_repository.list_pending_review(limit=limit, offset=offset)
    return [
        ReviewPendingArticle(
            id=article.id,
            title=article.title,
            summary=article.summary,
            status=article.status,
            created_at=article.created_at,
            category=article.category.name if article.category else None,
        )
        for article in articles
    ]


def approve_article(*, article_id: int, reviewer_id: int) -> ReviewActionResponse:
    """Aprova e publica um artigo."""
    reviewer = _ensure_reviewer(reviewer_id)
    article = article_repository.mark_as_reviewed(
        article_id=article_id,
        reviewer_id=reviewer.id,
        status="publicada",
    )
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo nao encontrado.")

    return ReviewActionResponse(
        article_id=article.id,
        status=article.status,
        reviewed_by=reviewer.id,
        reviewed_at=article.reviewed_at,
        published_at=article.published_at,
    )


def reject_article(*, article_id: int, reviewer_id: int) -> ReviewActionResponse:
    """Rejeita um artigo pendente."""
    reviewer = _ensure_reviewer(reviewer_id)
    article = article_repository.mark_as_reviewed(
        article_id=article_id,
        reviewer_id=reviewer.id,
        status="rejeitada",
    )
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo nao encontrado.")

    return ReviewActionResponse(
        article_id=article.id,
        status=article.status,
        reviewed_by=reviewer.id,
        reviewed_at=article.reviewed_at,
        published_at=article.published_at,
    )


def _ensure_reviewer(reviewer_id: int):
    """Garante que o usuario informado existe e pode revisar."""
    reviewer = user_repository.get_by_id(reviewer_id)
    if reviewer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revisor nao encontrado.")
    if reviewer.role != "revisor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O usuario informado nao possui permissao de revisor.",
        )
    return reviewer
