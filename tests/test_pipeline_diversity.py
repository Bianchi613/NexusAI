"""Testes de diversidade por fonte e categoria dentro do pipeline."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Engine.app.ai.ollama import GeneratedArticlePayload
from Engine.app.config import settings
from Engine.app.core.pipeline import NewsPipeline
from Engine.app.models import Base, NewsSource, RawArticle


def test_pipeline_selection_limits_same_source_to_three_articles() -> None:
    """Garante o teto de itens por fonte na selecao para geracao."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        source_a = NewsSource(name="RSS A", base_url="https://rss-a.example.com", source_type="rss", is_active=True)
        source_b = NewsSource(name="RSS B", base_url="https://rss-b.example.com", source_type="rss", is_active=True)
        session.add_all([source_a, source_b])
        session.flush()

        articles = [
            RawArticle(
                source_id=source_a.id,
                original_title=f"RSS A story {index} with enough content",
                original_url=f"https://rss-a.example.com/story-{index}",
            )
            for index in range(1, 7)
        ]
        articles.extend(
            [
                RawArticle(
                    source_id=source_b.id,
                    original_title=f"RSS B story {index} with enough content",
                    original_url=f"https://rss-b.example.com/story-{index}",
                )
                for index in range(1, 3)
            ]
        )

        pipeline = NewsPipeline()
        selected = pipeline._select_articles_for_run(session, articles, limit=8)

        assert sum(1 for article in selected if article.source_id == source_a.id) == 3
        assert sum(1 for article in selected if article.source_id == source_b.id) == 2


def test_pipeline_limits_raw_articles_per_source_to_three_varied_items() -> None:
    """Valida o limite de variedade por fonte ainda na etapa bruta."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    original_max_raw_per_source = settings.max_raw_articles_per_source
    settings.max_raw_articles_per_source = 3

    try:
        with SessionLocal() as session:
            source = NewsSource(name="RSS A", base_url="https://rss-a.example.com", source_type="rss", is_active=True)
            session.add(source)
            session.flush()

            articles = [
                RawArticle(
                    source_id=source.id,
                    original_title="Apple anuncia novo chip com foco em IA",
                    original_url="https://rss-a.example.com/story-1",
                    content_hash="hash-1",
                ),
                RawArticle(
                    source_id=source.id,
                    original_title="Apple anuncia novo chip para inteligencia artificial",
                    original_url="https://rss-a.example.com/story-2",
                    content_hash="hash-2",
                ),
                RawArticle(
                    source_id=source.id,
                    original_title="Congresso aprova nova politica industrial",
                    original_url="https://rss-a.example.com/story-3",
                    content_hash="hash-3",
                ),
                RawArticle(
                    source_id=source.id,
                    original_title="NASA prepara nova etapa da missao Artemis",
                    original_url="https://rss-a.example.com/story-4",
                    content_hash="hash-4",
                ),
                RawArticle(
                    source_id=source.id,
                    original_title="Hospital amplia atendimento de emergencia",
                    original_url="https://rss-a.example.com/story-5",
                    content_hash="hash-5",
                ),
            ]

            pipeline = NewsPipeline()
            limited = pipeline._limit_varied_articles_per_source(articles)

            assert len(limited) == 3
            assert [article.original_url for article in limited] == [
                "https://rss-a.example.com/story-1",
                "https://rss-a.example.com/story-3",
                "https://rss-a.example.com/story-4",
            ]
    finally:
        settings.max_raw_articles_per_source = original_max_raw_per_source


def test_pipeline_generation_defers_repeated_category_until_diversity_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """Adia categorias repetidas para manter diversidade minima no lote."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    original_max_per_category = settings.max_articles_per_category_per_run
    original_min_distinct = settings.min_distinct_categories_per_run

    settings.max_articles_per_category_per_run = 2
    settings.min_distinct_categories_per_run = 2

    try:
        with SessionLocal() as session:
            source = NewsSource(name="RSS A", base_url="https://rss-a.example.com", source_type="rss", is_active=True)
            session.add(source)
            session.flush()

            stored_articles = [
                RawArticle(
                    source_id=source.id,
                    original_title=f"Story {index} with enough content for generation",
                    original_url=f"https://rss-a.example.com/story-{index}",
                    original_description="Descricao longa o suficiente para o teste.",
                    original_content="Conteudo longo o suficiente para o teste de diversidade por categoria.",
                )
                for index in range(1, 5)
            ]
            session.add_all(stored_articles)
            session.commit()
            for article in stored_articles:
                session.refresh(article)

            payloads = [
                GeneratedArticlePayload("Titulo 1", "Resumo 1", "Corpo 1", "Tecnologia", ["IA"]),
                GeneratedArticlePayload("Titulo 2", "Resumo 2", "Corpo 2", "Tecnologia", ["IA"]),
                GeneratedArticlePayload("Titulo 3", "Resumo 3", "Corpo 3", "Tecnologia", ["IA"]),
                GeneratedArticlePayload("Titulo 4", "Resumo 4", "Corpo 4", "Politica", ["Congresso"]),
            ]

            pipeline = NewsPipeline()

            def fake_generate_article(raw_article, prompt_template):
                return payloads.pop(0)

            monkeypatch.setattr(pipeline.ai_client, "generate_article", fake_generate_article)

            generated = pipeline._generate_articles_for_run(session, stored_articles, "prompt", target_limit=3)

            assert len(generated) == 3
            categories = [article.category.name for article in generated if article.category is not None]
            assert categories == ["Tecnologia", "Politica", "Tecnologia"]
    finally:
        settings.max_articles_per_category_per_run = original_max_per_category
        settings.min_distinct_categories_per_run = original_min_distinct
