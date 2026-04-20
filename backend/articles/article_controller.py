"""Controller das rotas de artigos."""

from fastapi import HTTPException, status

from backend.articles.article_schema import (
    ArticleCreateRequest,
    ArticleDetailResponse,
    ArticleListItem,
    ArticleUpdateRequest,
)
from backend.articles.article_service import (
    create_article,
    delete_article,
    get_article,
    list_articles,
    update_article,
)


def list_portal_articles(
    *,
    limit: int,
    offset: int,
    status_filter: str | None = None,
    category_id: int | None = None,
    reviewed_by: int | None = None,
) -> list[ArticleListItem]:
    """Lista artigos para a camada HTTP."""
    return list_articles(
        limit=limit,
        offset=offset,
        status=status_filter,
        category_id=category_id,
        reviewed_by=reviewed_by,
    )


def get_portal_article(article_id: int) -> ArticleDetailResponse:
    """Retorna um artigo ou 404."""
    article = get_article(article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artigo nao encontrado.",
        )
    return article


def create_portal_article(payload: ArticleCreateRequest) -> ArticleDetailResponse:
    """Cria um artigo novo."""
    try:
        return create_article(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def update_portal_article(article_id: int, payload: ArticleUpdateRequest) -> ArticleDetailResponse:
    """Atualiza um artigo existente."""
    try:
        return update_article(article_id, payload)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def delete_portal_article(article_id: int) -> dict[str, str]:
    """Remove um artigo existente."""
    try:
        delete_article(article_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return {"detail": "Artigo removido com sucesso."}
