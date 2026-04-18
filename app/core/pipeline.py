import re
import unicodedata
from pathlib import Path
from typing import List

from app.ai.ollama import OllamaClient
from app.collectors.news_api import NewsAPICollector
from app.collectors.rss import RSSCollector
from app.config import settings
from app.db import get_session
from app.models import Category, GeneratedArticle, GeneratedArticleSource, RawArticle, Tag
from sqlalchemy import select


class NewsPipeline:
    def __init__(self) -> None:
        self.api_collector = NewsAPICollector()
        self.rss_collector = RSSCollector()
        self.ai_client = OllamaClient()
        self.prompt_path = Path("prompts/article.txt")

    def load_prompt(self) -> str:
        if not self.prompt_path.exists():
            return ""
        return self.prompt_path.read_text(encoding="utf-8")

    def run(self) -> List[GeneratedArticle]:
        prompt_template = self.load_prompt()
        generated_articles: List[GeneratedArticle] = []

        with get_session() as session:
            collected_articles = []
            collected_articles.extend(self.api_collector.collect(session))
            collected_articles.extend(self.rss_collector.collect(session))
            stored_articles = [self._persist_raw_article(session, article) for article in collected_articles]
            session.commit()

            for raw_article in stored_articles:
                if raw_article is None or self._already_generated(session, raw_article.id):
                    continue

                payload = self.ai_client.generate_article(raw_article, prompt_template)
                category = self._get_or_create_category(session, payload.category)
                tag_ids = self._get_or_create_tag_ids(session, payload.tags)

                generated_article = GeneratedArticle(
                    title=payload.title,
                    summary=payload.summary,
                    body=payload.body,
                    category_id=category.id if category else None,
                    status="nao_revisada",
                    ai_model=settings.ollama_model,
                    prompt_version=payload.prompt_version,
                    tags=tag_ids,
                )
                session.add(generated_article)
                session.flush()

                session.add(
                    GeneratedArticleSource(
                        generated_article_id=generated_article.id,
                        raw_article_id=raw_article.id,
                    )
                )
                session.commit()
                session.refresh(generated_article)
                generated_articles.append(generated_article)

        return generated_articles

    def _persist_raw_article(self, session, article: RawArticle) -> RawArticle:
        existing = session.scalar(
            select(RawArticle).where(
                (RawArticle.original_url == article.original_url) |
                (RawArticle.content_hash == article.content_hash)
            )
        )
        if existing is not None:
            return existing

        session.add(article)
        session.flush()
        return article

    def _already_generated(self, session, raw_article_id: int) -> bool:
        existing = session.scalar(
            select(GeneratedArticleSource).where(GeneratedArticleSource.raw_article_id == raw_article_id)
        )
        return existing is not None

    def _get_or_create_category(self, session, name: str) -> Category:
        normalized_name = (name or "geral").strip()
        slug = self._slugify(normalized_name)
        category = session.scalar(select(Category).where(Category.slug == slug))
        if category is not None:
            return category

        category = Category(name=normalized_name, slug=slug)
        session.add(category)
        session.flush()
        return category

    def _get_or_create_tag_ids(self, session, tag_names: List[str]) -> List[int]:
        tag_ids: List[int] = []

        for name in tag_names:
            normalized_name = name.strip()
            if not normalized_name:
                continue

            slug = self._slugify(normalized_name)
            tag = session.scalar(select(Tag).where(Tag.slug == slug))
            if tag is None:
                tag = Tag(name=normalized_name, slug=slug)
                session.add(tag)
                session.flush()

            tag_ids.append(tag.id)

        return tag_ids

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
        return slug or "geral"
