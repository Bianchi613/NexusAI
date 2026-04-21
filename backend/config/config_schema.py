"""Schemas das APIs agregadas da camada config."""

from pydantic import BaseModel

from backend.articles.article_read_schema import ArticleCardResponse
from backend.categories.category_read_schema import CategoryReadDetailResponse


class HomeResponse(BaseModel):
    """Blocos principais da home do portal."""

    latest_articles: list[ArticleCardResponse]
    watch_articles: list[ArticleCardResponse]
    featured_categories: list[CategoryReadDetailResponse]
