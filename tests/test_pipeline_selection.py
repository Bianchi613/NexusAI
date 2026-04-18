from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.pipeline import NewsPipeline
from app.models import Base, GeneratedArticle, NewsSource, RawArticle


def test_pipeline_selection_balances_source_types_before_repeating() -> None:
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
