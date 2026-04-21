"""Rotas de revisao editorial."""

from fastapi import APIRouter, Query

from backend.review.review_controller import (
    approve_review_article,
    create_review_article_controller,
    create_review_category_controller,
    create_review_tag_controller,
    delete_review_article_controller,
    delete_review_category_controller,
    delete_review_tag_controller,
    get_review_article_controller,
    get_review_category_controller,
    get_review_tag_controller,
    list_pending_review_articles,
    list_review_articles_controller,
    list_review_categories_controller,
    list_review_tags_controller,
    reject_review_article,
    update_review_article_controller,
    update_review_category_controller,
    update_review_tag_controller,
)
from backend.review.review_schema import (
    ReviewActionRequest,
    ReviewActionResponse,
    ReviewArticleCreateRequest,
    ReviewArticleDetailResponse,
    ReviewArticleListItem,
    ReviewArticleUpdateRequest,
    ReviewCategoryCreateRequest,
    ReviewCategoryDetailResponse,
    ReviewCategoryUpdateRequest,
    ReviewPendingArticle,
    ReviewTagCreateRequest,
    ReviewTagDetailResponse,
    ReviewTagUpdateRequest,
)


router = APIRouter(prefix="/review", tags=["Review"])


@router.get("/articles", response_model=list[ReviewArticleListItem])
def list_review_articles_route(
    reviewer_id: int = Query(..., ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: str | None = Query(default=None, alias="status"),
    category_id: int | None = Query(default=None, ge=1),
    reviewed_by: int | None = Query(default=None, ge=1),
) -> list[ReviewArticleListItem]:
    """Lista artigos no painel de revisao."""
    return list_review_articles_controller(
        reviewer_id=reviewer_id,
        limit=limit,
        offset=offset,
        status_filter=status_filter,
        category_id=category_id,
        reviewed_by=reviewed_by,
    )


@router.get("/articles/pending", response_model=list[ReviewPendingArticle])
def list_pending_articles_route(
    reviewer_id: int = Query(..., ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ReviewPendingArticle]:
    """Lista artigos pendentes de revisao."""
    return list_pending_review_articles(reviewer_id=reviewer_id, limit=limit, offset=offset)


@router.get("/articles/{article_id}", response_model=ReviewArticleDetailResponse)
def get_review_article_route(
    article_id: int,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewArticleDetailResponse:
    """Retorna um artigo para revisao."""
    return get_review_article_controller(reviewer_id=reviewer_id, article_id=article_id)


@router.post("/articles", response_model=ReviewArticleDetailResponse)
def create_review_article_route(
    payload: ReviewArticleCreateRequest,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewArticleDetailResponse:
    """Cria um artigo pela area de revisao."""
    return create_review_article_controller(reviewer_id=reviewer_id, payload=payload)


@router.put("/articles/{article_id}", response_model=ReviewArticleDetailResponse)
def update_review_article_route(
    article_id: int,
    payload: ReviewArticleUpdateRequest,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewArticleDetailResponse:
    """Atualiza um artigo pela area de revisao."""
    return update_review_article_controller(
        reviewer_id=reviewer_id,
        article_id=article_id,
        payload=payload,
    )


@router.delete("/articles/{article_id}", response_model=dict[str, str])
def delete_review_article_route(
    article_id: int,
    reviewer_id: int = Query(..., ge=1),
) -> dict[str, str]:
    """Remove um artigo pela area de revisao."""
    return delete_review_article_controller(reviewer_id=reviewer_id, article_id=article_id)


@router.patch("/articles/{article_id}/approve", response_model=ReviewActionResponse)
def approve_article_route(article_id: int, payload: ReviewActionRequest) -> ReviewActionResponse:
    """Aprova e publica um artigo."""
    return approve_review_article(article_id=article_id, reviewer_id=payload.reviewer_id)


@router.patch("/articles/{article_id}/reject", response_model=ReviewActionResponse)
def reject_article_route(article_id: int, payload: ReviewActionRequest) -> ReviewActionResponse:
    """Rejeita um artigo pendente."""
    return reject_review_article(article_id=article_id, reviewer_id=payload.reviewer_id)


@router.get("/categories", response_model=list[ReviewCategoryDetailResponse])
def list_review_categories_route(
    reviewer_id: int = Query(..., ge=1),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[ReviewCategoryDetailResponse]:
    """Lista categorias no painel de revisao."""
    return list_review_categories_controller(reviewer_id=reviewer_id, limit=limit, offset=offset)


@router.get("/categories/{category_id}", response_model=ReviewCategoryDetailResponse)
def get_review_category_route(
    category_id: int,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewCategoryDetailResponse:
    """Retorna uma categoria para revisao."""
    return get_review_category_controller(reviewer_id=reviewer_id, category_id=category_id)


@router.post("/categories", response_model=ReviewCategoryDetailResponse)
def create_review_category_route(
    payload: ReviewCategoryCreateRequest,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewCategoryDetailResponse:
    """Cria uma categoria pela area de revisao."""
    return create_review_category_controller(reviewer_id=reviewer_id, payload=payload)


@router.put("/categories/{category_id}", response_model=ReviewCategoryDetailResponse)
def update_review_category_route(
    category_id: int,
    payload: ReviewCategoryUpdateRequest,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewCategoryDetailResponse:
    """Atualiza uma categoria pela area de revisao."""
    return update_review_category_controller(
        reviewer_id=reviewer_id,
        category_id=category_id,
        payload=payload,
    )


@router.delete("/categories/{category_id}", response_model=dict[str, str])
def delete_review_category_route(
    category_id: int,
    reviewer_id: int = Query(..., ge=1),
) -> dict[str, str]:
    """Remove uma categoria pela area de revisao."""
    return delete_review_category_controller(reviewer_id=reviewer_id, category_id=category_id)


@router.get("/tags", response_model=list[ReviewTagDetailResponse])
def list_review_tags_route(
    reviewer_id: int = Query(..., ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[ReviewTagDetailResponse]:
    """Lista tags no painel de revisao."""
    return list_review_tags_controller(reviewer_id=reviewer_id, limit=limit, offset=offset)


@router.get("/tags/{tag_id}", response_model=ReviewTagDetailResponse)
def get_review_tag_route(
    tag_id: int,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewTagDetailResponse:
    """Retorna uma tag para revisao."""
    return get_review_tag_controller(reviewer_id=reviewer_id, tag_id=tag_id)


@router.post("/tags", response_model=ReviewTagDetailResponse)
def create_review_tag_route(
    payload: ReviewTagCreateRequest,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewTagDetailResponse:
    """Cria uma tag pela area de revisao."""
    return create_review_tag_controller(reviewer_id=reviewer_id, payload=payload)


@router.put("/tags/{tag_id}", response_model=ReviewTagDetailResponse)
def update_review_tag_route(
    tag_id: int,
    payload: ReviewTagUpdateRequest,
    reviewer_id: int = Query(..., ge=1),
) -> ReviewTagDetailResponse:
    """Atualiza uma tag pela area de revisao."""
    return update_review_tag_controller(reviewer_id=reviewer_id, tag_id=tag_id, payload=payload)


@router.delete("/tags/{tag_id}", response_model=dict[str, str])
def delete_review_tag_route(
    tag_id: int,
    reviewer_id: int = Query(..., ge=1),
) -> dict[str, str]:
    """Remove uma tag pela area de revisao."""
    return delete_review_tag_controller(reviewer_id=reviewer_id, tag_id=tag_id)
