"""Controller de revisao editorial."""

from backend.review.review_schema import ReviewActionResponse, ReviewPendingArticle
from backend.review.review_service import approve_article, list_pending_articles, reject_article


def list_pending_review_articles(limit: int, offset: int) -> list[ReviewPendingArticle]:
    """Lista artigos aguardando revisao."""
    return list_pending_articles(limit=limit, offset=offset)


def approve_review_article(article_id: int, reviewer_id: int) -> ReviewActionResponse:
    """Aprova um artigo pendente."""
    return approve_article(article_id=article_id, reviewer_id=reviewer_id)


def reject_review_article(article_id: int, reviewer_id: int) -> ReviewActionResponse:
    """Rejeita um artigo pendente."""
    return reject_article(article_id=article_id, reviewer_id=reviewer_id)

