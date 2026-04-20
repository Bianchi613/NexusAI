"""Servico de CRUD de artigos."""

from datetime import datetime, timezone

from backend.articles.article_repository import ArticleRepository
from backend.articles.article_schema import (
    ArticleCreateRequest,
    ArticleDetailResponse,
    ArticleListItem,
    ArticleUpdateRequest,
)


repository = ArticleRepository()


def _unique_ids(values: list[int]) -> list[int]:
    """Remove ids repetidos preservando a ordem."""
    unique_values: list[int] = []
    seen_values: set[int] = set()
    for value in values:
        if value in seen_values:
            continue
        seen_values.add(value)
        unique_values.append(value)
    return unique_values


def _clean_optional_text(value: str | None) -> str | None:
    """Limpa campos de texto opcionais."""
    if value is None:
        return None
    cleaned_value = value.strip()
    return cleaned_value or None


def _to_list_item(article) -> ArticleListItem:
    """Converte entidade ORM em resposta resumida."""
    return ArticleListItem(
        id=article.id,
        title=article.title,
        summary=article.summary,
        status=article.status,
        category_id=article.category_id,
        category=article.category.name if article.category else None,
        created_at=article.created_at,
        reviewed_at=article.reviewed_at,
        published_at=article.published_at,
        reviewed_by=article.reviewed_by,
        image_urls=list(article.image_urls or []),
        tag_ids=list(article.tags or []),
    )


def _to_detail_response(article) -> ArticleDetailResponse:
    """Converte entidade ORM em resposta detalhada."""
    return ArticleDetailResponse(
        id=article.id,
        title=article.title,
        summary=article.summary,
        body=article.body,
        status=article.status,
        category_id=article.category_id,
        category=article.category.name if article.category else None,
        ai_model=article.ai_model,
        prompt_version=article.prompt_version,
        created_at=article.created_at,
        reviewed_at=article.reviewed_at,
        published_at=article.published_at,
        reviewed_by=article.reviewed_by,
        image_urls=list(article.image_urls or []),
        video_urls=list(article.video_urls or []),
        tag_ids=list(article.tags or []),
        source_ids=list(article.source_ids or []),
    )


def _ensure_category_exists(category_id: int | None) -> None:
    """Valida categoria quando informada."""
    if category_id is None:
        return
    if not repository.category_exists(category_id):
        raise ValueError("Categoria informada nao existe.")


def _ensure_existing_tag_ids(tag_ids: list[int]) -> None:
    """Valida ids de tags."""
    existing_tag_ids = repository.existing_tag_ids(tag_ids)
    missing_tag_ids = [tag_id for tag_id in tag_ids if tag_id not in existing_tag_ids]
    if missing_tag_ids:
        raise ValueError(f"Tags inexistentes: {missing_tag_ids}.")


def _ensure_existing_source_ids(source_ids: list[int]) -> None:
    """Valida ids de noticias brutas vinculadas."""
    existing_source_ids = repository.existing_raw_article_ids(source_ids)
    missing_source_ids = [source_id for source_id in source_ids if source_id not in existing_source_ids]
    if missing_source_ids:
        raise ValueError(f"Raw articles inexistentes: {missing_source_ids}.")


def _resolve_review_fields(
    *,
    status: str,
    reviewed_by: int | None,
    current_article=None,
) -> dict[str, object]:
    """Deriva reviewed_at e published_at de acordo com o estado editorial."""
    if status == "nao_revisada":
        if reviewed_by is not None:
            raise ValueError("Artigo nao revisado nao pode receber reviewed_by.")
        return {
            "reviewed_by": None,
            "reviewed_at": None,
            "published_at": None,
        }

    if reviewed_by is None:
        raise ValueError("Artigos publicados ou rejeitados exigem um revisor.")

    reviewer = repository.get_reviewer(reviewed_by)
    if reviewer is None:
        raise ValueError("Revisor informado nao existe.")
    if reviewer.role != "revisor":
        raise ValueError("O usuario informado nao possui role de revisor.")

    now = datetime.now(timezone.utc)
    if current_article is None:
        reviewed_at = now
        published_at = now if status == "publicada" else None
    elif current_article.status == status and current_article.reviewed_by == reviewed_by:
        reviewed_at = current_article.reviewed_at or now
        published_at = (current_article.published_at or now) if status == "publicada" else None
    else:
        reviewed_at = now
        published_at = now if status == "publicada" else None

    return {
        "reviewed_by": reviewed_by,
        "reviewed_at": reviewed_at,
        "published_at": published_at,
    }


def list_articles(
    *,
    limit: int,
    offset: int,
    status: str | None = None,
    category_id: int | None = None,
    reviewed_by: int | None = None,
) -> list[ArticleListItem]:
    """Lista artigos com filtros opcionais."""
    articles = repository.list_all(
        limit=limit,
        offset=offset,
        status=status,
        category_id=category_id,
        reviewed_by=reviewed_by,
    )
    return [_to_list_item(article) for article in articles]


def get_article(article_id: int) -> ArticleDetailResponse | None:
    """Busca um artigo por id."""
    article = repository.get_by_id(article_id)
    if article is None:
        return None
    return _to_detail_response(article)


def create_article(payload: ArticleCreateRequest) -> ArticleDetailResponse:
    """Cria um artigo novo."""
    title = payload.title.strip()
    body = payload.body.strip()
    if not title:
        raise ValueError("Titulo do artigo e obrigatorio.")
    if not body:
        raise ValueError("Corpo do artigo e obrigatorio.")

    tag_ids = _unique_ids(list(payload.tag_ids or []))
    source_ids = _unique_ids(list(payload.source_ids or []))

    _ensure_category_exists(payload.category_id)
    _ensure_existing_tag_ids(tag_ids)
    _ensure_existing_source_ids(source_ids)

    review_fields = _resolve_review_fields(
        status=payload.status,
        reviewed_by=payload.reviewed_by,
    )

    article = repository.create(
        article_data={
            "title": title,
            "summary": _clean_optional_text(payload.summary),
            "body": body,
            "category_id": payload.category_id,
            "status": payload.status,
            "ai_model": _clean_optional_text(payload.ai_model),
            "prompt_version": _clean_optional_text(payload.prompt_version),
            "tags": tag_ids,
            "image_urls": list(payload.image_urls or []),
            "video_urls": list(payload.video_urls or []),
            **review_fields,
        },
        source_ids=source_ids,
    )
    return _to_detail_response(article)


def update_article(article_id: int, payload: ArticleUpdateRequest) -> ArticleDetailResponse:
    """Atualiza um artigo existente."""
    current_article = repository.get_by_id(article_id)
    if current_article is None:
        raise LookupError("Artigo nao encontrado.")

    payload_data = payload.model_dump(exclude_unset=True)

    source_ids = None
    if "source_ids" in payload_data:
        source_ids = _unique_ids(list(payload_data["source_ids"] or []))
        _ensure_existing_source_ids(source_ids)

    if "tag_ids" in payload_data:
        tag_ids = _unique_ids(list(payload_data["tag_ids"] or []))
    else:
        tag_ids = list(current_article.tags or [])
    _ensure_existing_tag_ids(tag_ids)

    if "category_id" in payload_data:
        category_id = payload_data["category_id"]
    else:
        category_id = current_article.category_id
    _ensure_category_exists(category_id)

    title_value = payload_data.get("title", current_article.title)
    if title_value is None:
        raise ValueError("Titulo do artigo e obrigatorio.")
    title = title_value.strip()
    if not title:
        raise ValueError("Titulo do artigo e obrigatorio.")

    body_value = payload_data.get("body", current_article.body)
    if body_value is None:
        raise ValueError("Corpo do artigo e obrigatorio.")
    body = body_value.strip()
    if not body:
        raise ValueError("Corpo do artigo e obrigatorio.")

    status = payload_data.get("status", current_article.status)
    reviewed_by = payload_data.get("reviewed_by", current_article.reviewed_by)
    review_fields = _resolve_review_fields(
        status=status,
        reviewed_by=reviewed_by,
        current_article=current_article,
    )

    updated_article = repository.update(
        article_id=article_id,
        article_data={
            "title": title,
            "summary": _clean_optional_text(
                payload_data["summary"] if "summary" in payload_data else current_article.summary
            ),
            "body": body,
            "category_id": category_id,
            "status": status,
            "ai_model": _clean_optional_text(
                payload_data["ai_model"] if "ai_model" in payload_data else current_article.ai_model
            ),
            "prompt_version": _clean_optional_text(
                payload_data["prompt_version"]
                if "prompt_version" in payload_data
                else current_article.prompt_version
            ),
            "tags": tag_ids,
            "image_urls": list(
                payload_data["image_urls"] if "image_urls" in payload_data else current_article.image_urls or []
            ),
            "video_urls": list(
                payload_data["video_urls"] if "video_urls" in payload_data else current_article.video_urls or []
            ),
            **review_fields,
        },
        source_ids=source_ids,
    )
    if updated_article is None:
        raise LookupError("Artigo nao encontrado.")

    return _to_detail_response(updated_article)


def delete_article(article_id: int) -> None:
    """Remove um artigo existente."""
    deleted = repository.delete(article_id)
    if not deleted:
        raise LookupError("Artigo nao encontrado.")
