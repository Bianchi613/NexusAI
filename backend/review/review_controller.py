"""Controller de revisao editorial."""

from backend.review.review_schema import (
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
from backend.review.review_service import (
    approve_article,
    create_review_article,
    create_review_category,
    create_review_tag,
    delete_review_article,
    delete_review_category,
    delete_review_tag,
    get_review_article,
    get_review_category,
    get_review_tag,
    list_pending_articles,
    list_review_articles,
    list_review_categories,
    list_review_tags,
    reject_article,
    update_review_article,
    update_review_category,
    update_review_tag,
)


def list_pending_review_articles(*, reviewer_id: int, limit: int, offset: int) -> list[ReviewPendingArticle]:
    """Lista artigos aguardando revisao."""
    return list_pending_articles(reviewer_id=reviewer_id, limit=limit, offset=offset)


def list_review_articles_controller(
    *,
    reviewer_id: int,
    limit: int,
    offset: int,
    status_filter: str | None = None,
    category_id: int | None = None,
    reviewed_by: int | None = None,
) -> list[ReviewArticleListItem]:
    """Lista artigos no painel de revisao."""
    return list_review_articles(
        reviewer_id=reviewer_id,
        limit=limit,
        offset=offset,
        status_filter=status_filter,
        category_id=category_id,
        reviewed_by=reviewed_by,
    )


def get_review_article_controller(*, reviewer_id: int, article_id: int) -> ReviewArticleDetailResponse:
    """Retorna um artigo para revisao."""
    return get_review_article(reviewer_id=reviewer_id, article_id=article_id)


def create_review_article_controller(
    *,
    reviewer_id: int,
    payload: ReviewArticleCreateRequest,
) -> ReviewArticleDetailResponse:
    """Cria um artigo pelo painel de revisao."""
    return create_review_article(reviewer_id=reviewer_id, payload=payload)


def update_review_article_controller(
    *,
    reviewer_id: int,
    article_id: int,
    payload: ReviewArticleUpdateRequest,
) -> ReviewArticleDetailResponse:
    """Atualiza um artigo pelo painel de revisao."""
    return update_review_article(reviewer_id=reviewer_id, article_id=article_id, payload=payload)


def delete_review_article_controller(*, reviewer_id: int, article_id: int) -> dict[str, str]:
    """Remove um artigo pelo painel de revisao."""
    delete_review_article(reviewer_id=reviewer_id, article_id=article_id)
    return {"detail": "Artigo removido com sucesso."}


def approve_review_article(article_id: int, reviewer_id: int) -> ReviewActionResponse:
    """Aprova um artigo pendente."""
    return approve_article(article_id=article_id, reviewer_id=reviewer_id)


def reject_review_article(article_id: int, reviewer_id: int) -> ReviewActionResponse:
    """Rejeita um artigo pendente."""
    return reject_article(article_id=article_id, reviewer_id=reviewer_id)


def list_review_categories_controller(*, reviewer_id: int, limit: int, offset: int) -> list[ReviewCategoryDetailResponse]:
    """Lista categorias no painel de revisao."""
    return list_review_categories(reviewer_id=reviewer_id, limit=limit, offset=offset)


def get_review_category_controller(*, reviewer_id: int, category_id: int) -> ReviewCategoryDetailResponse:
    """Retorna uma categoria para revisao."""
    return get_review_category(reviewer_id=reviewer_id, category_id=category_id)


def create_review_category_controller(
    *,
    reviewer_id: int,
    payload: ReviewCategoryCreateRequest,
) -> ReviewCategoryDetailResponse:
    """Cria uma categoria pelo painel de revisao."""
    return create_review_category(reviewer_id=reviewer_id, payload=payload)


def update_review_category_controller(
    *,
    reviewer_id: int,
    category_id: int,
    payload: ReviewCategoryUpdateRequest,
) -> ReviewCategoryDetailResponse:
    """Atualiza uma categoria pelo painel de revisao."""
    return update_review_category(reviewer_id=reviewer_id, category_id=category_id, payload=payload)


def delete_review_category_controller(*, reviewer_id: int, category_id: int) -> dict[str, str]:
    """Remove uma categoria pelo painel de revisao."""
    delete_review_category(reviewer_id=reviewer_id, category_id=category_id)
    return {"detail": "Categoria removida com sucesso."}


def list_review_tags_controller(*, reviewer_id: int, limit: int, offset: int) -> list[ReviewTagDetailResponse]:
    """Lista tags no painel de revisao."""
    return list_review_tags(reviewer_id=reviewer_id, limit=limit, offset=offset)


def get_review_tag_controller(*, reviewer_id: int, tag_id: int) -> ReviewTagDetailResponse:
    """Retorna uma tag para revisao."""
    return get_review_tag(reviewer_id=reviewer_id, tag_id=tag_id)


def create_review_tag_controller(
    *,
    reviewer_id: int,
    payload: ReviewTagCreateRequest,
) -> ReviewTagDetailResponse:
    """Cria uma tag pelo painel de revisao."""
    return create_review_tag(reviewer_id=reviewer_id, payload=payload)


def update_review_tag_controller(
    *,
    reviewer_id: int,
    tag_id: int,
    payload: ReviewTagUpdateRequest,
) -> ReviewTagDetailResponse:
    """Atualiza uma tag pelo painel de revisao."""
    return update_review_tag(reviewer_id=reviewer_id, tag_id=tag_id, payload=payload)


def delete_review_tag_controller(*, reviewer_id: int, tag_id: int) -> dict[str, str]:
    """Remove uma tag pelo painel de revisao."""
    delete_review_tag(reviewer_id=reviewer_id, tag_id=tag_id)
    return {"detail": "Tag removida com sucesso."}
