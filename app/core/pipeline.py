import re
from pathlib import Path
from typing import List

from app.ai.ollama import OllamaClient
from app.collectors.news_api import NewsAPICollector
from app.collectors.rss import RSSCollector
from app.config import settings
from app.core.article_filters import normalize_label, normalize_title, normalize_url, slugify
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
            collected_articles = self._deduplicate_batch(collected_articles)
            if settings.pipeline_max_items_per_run > 0:
                collected_articles = collected_articles[: settings.pipeline_max_items_per_run]
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
        article_url = normalize_url(article.original_url)
        article_title = normalize_title(article.original_title)
        existing_articles = session.scalars(select(RawArticle)).all()

        for existing in existing_articles:
            if article.content_hash and existing.content_hash == article.content_hash:
                return existing
            if article_url and normalize_url(existing.original_url) == article_url:
                return existing
            if article_title and normalize_title(existing.original_title) == article_title:
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
        normalized_name = self._normalize_category_name(name)
        slug = slugify(normalized_name)
        category = session.scalar(select(Category).where(Category.slug == slug))
        if category is not None:
            return category

        category = Category(name=normalized_name, slug=slug)
        session.add(category)
        session.flush()
        return category

    def _get_or_create_tag_ids(self, session, tag_names: List[str]) -> List[int]:
        tag_ids: List[int] = []
        seen_slugs: set[str] = set()

        for name in tag_names[: settings.max_tags_per_article]:
            normalized_name = normalize_label(name)
            if not normalized_name:
                continue

            slug = slugify(normalized_name)
            if slug in seen_slugs:
                continue

            seen_slugs.add(slug)
            tag = session.scalar(select(Tag).where(Tag.slug == slug))
            if tag is None:
                tag = Tag(name=normalized_name, slug=slug)
                session.add(tag)
                session.flush()

            tag_ids.append(tag.id)

        return tag_ids

    def _normalize_category_name(self, name: str) -> str:
        normalized_name = normalize_label(name or "Geral") or "Geral"
        allowed_by_slug = {slugify(category): category for category in settings.allowed_categories}
        return allowed_by_slug.get(slugify(normalized_name), "Geral")

    def _deduplicate_batch(self, articles: List[RawArticle]) -> List[RawArticle]:
        unique_articles: List[RawArticle] = []
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()
        seen_hashes: set[str] = set()

        for article in articles:
            normalized_url = normalize_url(article.original_url)
            normalized_title = normalize_title(article.original_title)
            content_hash = article.content_hash or ""

            if normalized_url and normalized_url in seen_urls:
                continue
            if normalized_title and normalized_title in seen_titles:
                continue
            if content_hash and content_hash in seen_hashes:
                continue

            if normalized_url:
                seen_urls.add(normalized_url)
            if normalized_title:
                seen_titles.add(normalized_title)
            if content_hash:
                seen_hashes.add(content_hash)

            unique_articles.append(article)

        return unique_articles
