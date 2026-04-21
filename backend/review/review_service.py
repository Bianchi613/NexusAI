"""Servico de revisao editorial."""

from fastapi import HTTPException, status

from backend.articles.article_schema import ArticleCreateRequest, ArticleDetailResponse, ArticleListItem, ArticleUpdateRequest
from backend.articles.article_repository import ArticleRepository
from backend.articles.article_service import create_article, delete_article, get_article, list_articles, update_article
from backend.categories.category_schema import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest
from backend.categories.category_service import create_category, delete_category, get_category, list_categories, update_category
from backend.review.review_schema import ReviewActionResponse, ReviewPendingArticle
from backend.tags.tag_schema import TagCreateRequest, TagResponse, TagUpdateRequest
from backend.tags.tag_service import create_tag, delete_tag, get_tag, list_tags, update_tag
from backend.users.user_repository import UserRepository

article_repository = ArticleRepository()
user_repository = UserRepository()


def list_pending_articles(*, reviewer_id: int, limit: int, offset: int) -> list[ReviewPendingArticle]:
    """Lista artigos que aguardam revisao."""
    _ensure_reviewer(reviewer_id)
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


def list_review_articles(
    *,
    reviewer_id: int,
    limit: int,
    offset: int,
    status_filter: str | None = None,
    category_id: int | None = None,
    reviewed_by: int | None = None,
) -> list[ArticleListItem]:
    """Lista artigos para o painel de revisao."""
    _ensure_reviewer(reviewer_id)
    return list_articles(
        limit=limit,
        offset=offset,
        status=status_filter,
        category_id=category_id,
        reviewed_by=reviewed_by,
    )


def get_review_article(*, reviewer_id: int, article_id: int) -> ArticleDetailResponse:
    """Retorna um artigo para revisao."""
    _ensure_reviewer(reviewer_id)
    article = get_article(article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo nao encontrado.")
    return article


def create_review_article(*, reviewer_id: int, payload: ArticleCreateRequest) -> ArticleDetailResponse:
    """Cria um artigo pela area de revisao."""
    reviewer = _ensure_reviewer(reviewer_id)
    payload = _fill_reviewed_by_when_missing(payload, reviewer.id)
    try:
        return create_article(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def update_review_article(*, reviewer_id: int, article_id: int, payload: ArticleUpdateRequest) -> ArticleDetailResponse:
    """Atualiza um artigo pela area de revisao."""
    reviewer = _ensure_reviewer(reviewer_id)
    payload = _fill_reviewed_by_when_missing(payload, reviewer.id)
    try:
        return update_article(article_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def delete_review_article(*, reviewer_id: int, article_id: int) -> None:
    """Remove um artigo pela area de revisao."""
    _ensure_reviewer(reviewer_id)
    try:
        delete_article(article_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


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


def list_review_categories(*, reviewer_id: int, limit: int, offset: int) -> list[CategoryResponse]:
    """Lista categorias para o painel de revisao."""
    _ensure_reviewer(reviewer_id)
    return list_categories(limit=limit, offset=offset)


def get_review_category(*, reviewer_id: int, category_id: int) -> CategoryResponse:
    """Retorna uma categoria para revisao."""
    _ensure_reviewer(reviewer_id)
    category = get_category(category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria nao encontrada.")
    return category


def create_review_category(*, reviewer_id: int, payload: CategoryCreateRequest) -> CategoryResponse:
    """Cria uma categoria pela area de revisao."""
    _ensure_reviewer(reviewer_id)
    try:
        return create_category(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


def update_review_category(
    *,
    reviewer_id: int,
    category_id: int,
    payload: CategoryUpdateRequest,
) -> CategoryResponse:
    """Atualiza uma categoria pela area de revisao."""
    _ensure_reviewer(reviewer_id)
    try:
        return update_category(category_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


def delete_review_category(*, reviewer_id: int, category_id: int) -> None:
    """Remove uma categoria pela area de revisao."""
    _ensure_reviewer(reviewer_id)
    try:
        delete_category(category_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def list_review_tags(*, reviewer_id: int, limit: int, offset: int) -> list[TagResponse]:
    """Lista tags para o painel de revisao."""
    _ensure_reviewer(reviewer_id)
    return list_tags(limit=limit, offset=offset)


def get_review_tag(*, reviewer_id: int, tag_id: int) -> TagResponse:
    """Retorna uma tag para revisao."""
    _ensure_reviewer(reviewer_id)
    tag = get_tag(tag_id)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag nao encontrada.")
    return tag


def create_review_tag(*, reviewer_id: int, payload: TagCreateRequest) -> TagResponse:
    """Cria uma tag pela area de revisao."""
    _ensure_reviewer(reviewer_id)
    try:
        return create_tag(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


def update_review_tag(*, reviewer_id: int, tag_id: int, payload: TagUpdateRequest) -> TagResponse:
    """Atualiza uma tag pela area de revisao."""
    _ensure_reviewer(reviewer_id)
    try:
        return update_tag(tag_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


def delete_review_tag(*, reviewer_id: int, tag_id: int) -> None:
    """Remove uma tag pela area de revisao."""
    _ensure_reviewer(reviewer_id)
    try:
        delete_tag(tag_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _fill_reviewed_by_when_missing(payload, reviewer_id: int):
    """Preenche reviewed_by automaticamente quando o revisor altera status final."""
    payload_data = payload.model_dump(exclude_unset=True)
    status_value = payload_data.get("status")
    if status_value in {"publicada", "rejeitada"} and payload_data.get("reviewed_by") is None:
        return payload.model_copy(update={"reviewed_by": reviewer_id})
    return payload


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
