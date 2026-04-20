"""Servico de leitura publica de artigos."""

from backend.articles.article_repository import ArticleRepository
from backend.articles.article_schema import ArticleDetailResponse, ArticleListItem


repository = ArticleRepository()


def fetch_published_articles(limit: int, offset: int) -> list[ArticleListItem]:
    """Busca artigos publicados e adapta para resposta publica."""
    articles = repository.list_published(limit=limit, offset=offset)
    return [
        ArticleListItem(
            id=article.id,
            title=article.title,
            summary=article.summary,
            category=article.category.name if article.category else None,
            published_at=article.published_at,
            image_urls=list(article.image_urls or []),
        )
        for article in articles
    ]


def fetch_published_article(article_id: int) -> ArticleDetailResponse | None:
    """Retorna o detalhe de um artigo publicado."""
    article = repository.get_published_by_id(article_id)
    if article is None:
        return None

    return ArticleDetailResponse(
        id=article.id,
        title=article.title,
        summary=article.summary,
        body=article.body,
        category=article.category.name if article.category else None,
        published_at=article.published_at,
        image_urls=list(article.image_urls or []),
        video_urls=list(article.video_urls or []),
        tag_ids=list(article.tags or []),
    )
