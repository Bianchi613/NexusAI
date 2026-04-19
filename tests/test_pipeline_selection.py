"""Testes da logica de selecao e rotacao de candidatos do pipeline."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
import app.core.pipeline as pipeline_module
from app.ai.ollama import GeneratedArticlePayload
from app.core.pipeline import NewsPipeline
from app.models import Base, GeneratedArticle, NewsSource, RawArticle


def test_pipeline_selection_balances_source_types_before_repeating() -> None:
    """A selecao tenta variar tipo de fonte antes de repetir o mesmo tipo."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        api_source = NewsSource(name="API One", base_url="https://api.example.com", source_type="api", is_active=True)
        rss_source_a = NewsSource(name="RSS One", base_url="https://rss-a.example.com", source_type="rss", is_active=True)
        rss_source_b = NewsSource(name="RSS Two", base_url="https://rss-b.example.com", source_type="rss", is_active=True)
        json_source = NewsSource(
            name="JSON One",
            base_url="https://json.example.com/feed.json",
            source_type="json_feed",
            is_active=True,
        )
        session.add_all([api_source, rss_source_a, rss_source_b, json_source])
        session.flush()

        articles = [
            RawArticle(
                source_id=api_source.id,
                original_title="API story one with enough content for selection",
                original_url="https://api.example.com/story-1",
            ),
            RawArticle(
                source_id=rss_source_a.id,
                original_title="RSS story one with enough content for selection",
                original_url="https://rss-a.example.com/story-1",
            ),
            RawArticle(
                source_id=rss_source_b.id,
                original_title="RSS story two with enough content for selection",
                original_url="https://rss-b.example.com/story-1",
            ),
            RawArticle(
                source_id=json_source.id,
                original_title="JSON story one with enough content for selection",
                original_url="https://json.example.com/story-1",
            ),
            RawArticle(
                source_id=rss_source_a.id,
                original_title="RSS story one second item with enough content",
                original_url="https://rss-a.example.com/story-2",
            ),
        ]

        pipeline = NewsPipeline()
        selected = pipeline._select_articles_for_run(session, articles, limit=4)
        selected_types = {
            source.id: source.source_type
            for source in session.query(NewsSource).all()
        }
        type_sequence = [selected_types[article.source_id] for article in selected]

        assert len(selected) == 4
        assert type_sequence[:3] == ["api", "rss", "json_feed"]
        assert type_sequence[3] == "rss"


def test_pipeline_selection_rotates_types_on_later_runs() -> None:
    """Em rodadas seguintes, a ordem de tipos deve rotacionar."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        session.add(GeneratedArticle(title="existing", body="existing body", status="nao_revisada", tags=[]))
        session.flush()

        rss_source = NewsSource(name="RSS One", base_url="https://rss.example.com", source_type="rss", is_active=True)
        json_source = NewsSource(
            name="JSON One",
            base_url="https://json.example.com/feed.json",
            source_type="json_feed",
            is_active=True,
        )
        session.add_all([rss_source, json_source])
        session.flush()

        articles = [
            RawArticle(
                source_id=rss_source.id,
                original_title="RSS story one with enough content for selection",
                original_url="https://rss.example.com/story-1",
            ),
            RawArticle(
                source_id=json_source.id,
                original_title="JSON story one with enough content for selection",
                original_url="https://json.example.com/story-1",
            ),
        ]

        pipeline = NewsPipeline()
        selected = pipeline._select_articles_for_run(session, articles, limit=1)

        assert [article.source_id for article in selected] == [json_source.id]


def test_pipeline_candidate_limit_uses_small_buffer_for_generation() -> None:
    """O pool de candidatos deve respeitar multiplicador e buffer configurados."""
    original_multiplier = settings.pipeline_candidate_pool_multiplier
    original_buffer = settings.pipeline_generation_buffer

    settings.pipeline_candidate_pool_multiplier = 1
    settings.pipeline_generation_buffer = 4

    try:
        pipeline = NewsPipeline()
        assert pipeline._get_candidate_limit(total_articles=100, target_limit=12) == 16
        assert pipeline._get_candidate_limit(total_articles=10, target_limit=12) == 10
    finally:
        settings.pipeline_candidate_pool_multiplier = original_multiplier
        settings.pipeline_generation_buffer = original_buffer


def test_pipeline_run_persists_all_raw_articles_before_limiting_generation(monkeypatch) -> None:
    """Mesmo com limite de geracao, o bruto valido precisa ser persistido antes."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with SessionLocal() as seed_session:
        source = NewsSource(name="RSS One", base_url="https://rss.example.com", source_type="rss", is_active=True)
        seed_session.add(source)
        seed_session.commit()
        seed_session.refresh(source)
        source_id = source.id

    @contextmanager
    def fake_get_session():
        with SessionLocal() as session:
            yield session

    monkeypatch.setattr(pipeline_module, "get_session", fake_get_session)

    original_limit = settings.pipeline_max_items_per_run
    original_multiplier = settings.pipeline_candidate_pool_multiplier
    original_buffer = settings.pipeline_generation_buffer
    original_max_raw_per_source = settings.max_raw_articles_per_source

    settings.pipeline_max_items_per_run = 2
    settings.pipeline_candidate_pool_multiplier = 1
    settings.pipeline_generation_buffer = 0
    settings.max_raw_articles_per_source = 3

    try:
        article_titles = [
            "Congresso aprova projeto de educacao digital nas escolas",
            "Apple apresenta novo iPhone com foco em inteligencia artificial",
            "Mercado reage a anuncio de juros pelo banco central",
            "NASA divulga nova etapa da missao Artemis",
            "Hospital amplia atendimento de emergencia no interior",
        ]
        articles = [
            RawArticle(
                source_id=source_id,
                original_title=title,
                original_url=f"https://rss.example.com/story-{index}",
                original_description="Descricao suficiente para o teste.",
                original_content="Conteudo suficiente para o teste do fluxo completo.",
            )
            for index, title in enumerate(article_titles, start=1)
        ]

        pipeline = NewsPipeline()
        monkeypatch.setattr(pipeline.api_collector, "collect", lambda session: [])
        monkeypatch.setattr(pipeline.rss_collector, "collect", lambda session: list(articles))
        monkeypatch.setattr(pipeline.json_feed_collector, "collect", lambda session: [])

        payloads = [
            GeneratedArticlePayload("Titulo 1", "Resumo 1", "Corpo 1", "Tecnologia", ["IA"]),
            GeneratedArticlePayload("Titulo 2", "Resumo 2", "Corpo 2", "Politica", ["Congresso"]),
        ]

        monkeypatch.setattr(pipeline.ai_client, "generate_article", lambda raw_article, prompt: payloads.pop(0))

        generated = pipeline.run()

        with SessionLocal() as verify_session:
            raw_count = verify_session.query(RawArticle).count()
            generated_count = verify_session.query(GeneratedArticle).count()

        assert raw_count == 3
        assert generated_count == 2
        assert len(generated) == 2
    finally:
        settings.pipeline_max_items_per_run = original_limit
        settings.pipeline_candidate_pool_multiplier = original_multiplier
        settings.pipeline_generation_buffer = original_buffer
        settings.max_raw_articles_per_source = original_max_raw_per_source
