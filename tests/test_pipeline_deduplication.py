"""Testes das regras de deduplicacao do pipeline sobre `raw_articles`."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Engine.app.config import settings
from Engine.app.core.pipeline import NewsPipeline
from Engine.app.models import Base, NewsSource, RawArticle


def test_persist_raw_article_blocks_same_url_globally() -> None:
    """A URL continua sendo deduplicada globalmente, mesmo fora do lookback."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        source = NewsSource(name="Fonte", base_url="https://example.com/feed", source_type="rss", is_active=True)
        session.add(source)
        session.flush()

        existing = RawArticle(
            source_id=source.id,
            original_title="Titulo antigo",
            original_url="https://example.com/noticia-1",
            collected_at=datetime.now(timezone.utc) - timedelta(days=120),
        )
        session.add(existing)
        session.commit()
        session.refresh(existing)

        incoming = RawArticle(
            source_id=source.id,
            original_title="Titulo novo",
            original_url="https://example.com/noticia-1",
        )

        pipeline = NewsPipeline()
        persisted = pipeline._persist_raw_article(session, incoming)

        assert persisted.id == existing.id


def test_persist_raw_article_blocks_recent_duplicate_title_only_within_lookback() -> None:
    """Titulo igual recente bloqueia; titulo antigo fora da janela nao bloqueia."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    original_lookback_days = settings.deduplication_lookback_days
    settings.deduplication_lookback_days = 15

    try:
        with SessionLocal() as session:
            source = NewsSource(name="Fonte", base_url="https://example.com/feed", source_type="rss", is_active=True)
            session.add(source)
            session.flush()

            recent_article = RawArticle(
                source_id=source.id,
                original_title="Mercado reage a novo anuncio do banco central",
                original_url="https://example.com/noticia-recente",
                collected_at=datetime.now(timezone.utc) - timedelta(days=3),
            )
            old_article = RawArticle(
                source_id=source.id,
                original_title="Empresa amplia producao de chips em fabrica local",
                original_url="https://example.com/noticia-antiga",
                collected_at=datetime.now(timezone.utc) - timedelta(days=30),
            )
            session.add_all([recent_article, old_article])
            session.commit()
            session.refresh(recent_article)
            session.refresh(old_article)

            pipeline = NewsPipeline()

            duplicate_recent_title = RawArticle(
                source_id=source.id,
                original_title="Mercado reage a novo anúncio do Banco Central",
                original_url="https://example.com/url-diferente-1",
            )
            persisted_recent = pipeline._persist_raw_article(session, duplicate_recent_title)

            duplicate_old_title = RawArticle(
                source_id=source.id,
                original_title="Empresa amplia produção de chips em fábrica local",
                original_url="https://example.com/url-diferente-2",
            )
            persisted_old = pipeline._persist_raw_article(session, duplicate_old_title)
            session.commit()

            assert persisted_recent.id == recent_article.id
            assert persisted_old.id != old_article.id
            assert persisted_old.original_url == "https://example.com/url-diferente-2"
    finally:
        settings.deduplication_lookback_days = original_lookback_days


def test_persist_raw_article_blocks_recent_duplicate_content_hash_only_within_lookback() -> None:
    """`content_hash` recente bloqueia; fora do lookback nao bloqueia."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    original_lookback_days = settings.deduplication_lookback_days
    settings.deduplication_lookback_days = 15

    try:
        with SessionLocal() as session:
            source = NewsSource(name="Fonte", base_url="https://example.com/feed", source_type="rss", is_active=True)
            session.add(source)
            session.flush()

            recent_article = RawArticle(
                source_id=source.id,
                original_title="Titulo recente",
                original_url="https://example.com/recente",
                content_hash="hash-recente",
                collected_at=datetime.now(timezone.utc) - timedelta(days=2),
            )
            old_article = RawArticle(
                source_id=source.id,
                original_title="Titulo antigo",
                original_url="https://example.com/antiga",
                content_hash="hash-antiga",
                collected_at=datetime.now(timezone.utc) - timedelta(days=40),
            )
            session.add_all([recent_article, old_article])
            session.commit()
            session.refresh(recent_article)
            session.refresh(old_article)

            pipeline = NewsPipeline()

            duplicate_recent_hash = RawArticle(
                source_id=source.id,
                original_title="Outro titulo recente",
                original_url="https://example.com/url-diferente-3",
                content_hash="hash-recente",
            )
            persisted_recent = pipeline._persist_raw_article(session, duplicate_recent_hash)

            duplicate_old_hash = RawArticle(
                source_id=source.id,
                original_title="Outro titulo antigo",
                original_url="https://example.com/url-diferente-4",
                content_hash="hash-antiga",
            )
            persisted_old = pipeline._persist_raw_article(session, duplicate_old_hash)
            session.commit()

            assert persisted_recent.id == recent_article.id
            assert persisted_old.id != old_article.id
            assert persisted_old.original_url == "https://example.com/url-diferente-4"
    finally:
        settings.deduplication_lookback_days = original_lookback_days


def test_prepare_generation_candidates_excludes_similar_articles_inside_same_batch() -> None:
    """Remove quase-duplicatas do mesmo lote antes da geracao final."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        source_a = NewsSource(name="Fonte A", base_url="https://a.com/feed", source_type="rss", is_active=True)
        source_b = NewsSource(name="Fonte B", base_url="https://b.com/feed", source_type="rss", is_active=True)
        session.add_all([source_a, source_b])
        session.flush()

        article_a = RawArticle(
            source_id=source_a.id,
            original_title="Apple anuncia novo iPhone com recursos de inteligencia artificial",
            original_url="https://a.com/apple-iphone",
            content_hash="hash-a",
        )
        article_b = RawArticle(
            source_id=source_b.id,
            original_title="Apple anuncia novo iPhone com recurso de IA",
            original_url="https://b.com/apple-iphone-ia",
            content_hash="hash-b",
        )
        article_c = RawArticle(
            source_id=source_b.id,
            original_title="Congresso aprova novo projeto de lei sobre educacao",
            original_url="https://b.com/congresso-educacao",
            content_hash="hash-c",
        )
        session.add_all([article_a, article_b, article_c])
        session.commit()
        session.refresh(article_a)
        session.refresh(article_b)
        session.refresh(article_c)

        pipeline = NewsPipeline()
        prepared = pipeline._prepare_generation_candidates(session, [article_a, article_b, article_c], target_limit=5)

        prepared_ids = {article.id for article in prepared}
        assert article_c.id in prepared_ids
        assert len(prepared_ids & {article_a.id, article_b.id}) == 1
