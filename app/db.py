from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Base


engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_database_url() -> str:
    return settings.database_url


def get_session() -> Session:
    return SessionLocal()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _sync_runtime_schema()


def _sync_runtime_schema() -> None:
    inspector = inspect(engine)

    if "news_sources" not in inspector.get_table_names():
        return

    with engine.begin() as connection:
        if engine.dialect.name == "postgresql":
            connection.execute(text("ALTER TABLE news_sources DROP CONSTRAINT IF EXISTS ck_news_sources_type"))
            connection.execute(
                text(
                    "ALTER TABLE news_sources "
                    "ADD CONSTRAINT ck_news_sources_type "
                    "CHECK (source_type IN ('api', 'rss', 'json_feed'))"
                )
            )
            connection.execute(
                text(
                    "ALTER TABLE raw_articles "
                    "ADD COLUMN IF NOT EXISTS original_image_urls JSON NOT NULL DEFAULT '[]'::json"
                )
            )
            connection.execute(
                text(
                    "ALTER TABLE raw_articles "
                    "ADD COLUMN IF NOT EXISTS original_video_urls JSON NOT NULL DEFAULT '[]'::json"
                )
            )
            connection.execute(
                text(
                    "UPDATE raw_articles "
                    "SET original_image_urls = CASE "
                    "WHEN original_image_url IS NOT NULL AND btrim(original_image_url) <> '' "
                    "THEN json_build_array(original_image_url) "
                    "ELSE COALESCE(original_image_urls, '[]'::json) END "
                    "WHERE original_image_urls IS NULL OR original_image_urls::text = '[]'"
                )
            )

            connection.execute(
                text(
                    "ALTER TABLE generated_articles "
                    "ADD COLUMN IF NOT EXISTS image_urls JSON NOT NULL DEFAULT '[]'::json"
                )
            )
            connection.execute(
                text(
                    "ALTER TABLE generated_articles "
                    "ADD COLUMN IF NOT EXISTS video_urls JSON NOT NULL DEFAULT '[]'::json"
                )
            )
            connection.execute(
                text(
                    "UPDATE generated_articles ga "
                    "SET image_urls = COALESCE(ra.original_image_urls, '[]'::json) "
                    "FROM generated_article_sources gas "
                    "JOIN raw_articles ra ON ra.id = gas.raw_article_id "
                    "WHERE gas.generated_article_id = ga.id "
                    "AND (ga.image_urls IS NULL OR ga.image_urls::text = '[]')"
                )
            )
            connection.execute(
                text(
                    "UPDATE generated_articles ga "
                    "SET video_urls = COALESCE(ra.original_video_urls, '[]'::json) "
                    "FROM generated_article_sources gas "
                    "JOIN raw_articles ra ON ra.id = gas.raw_article_id "
                    "WHERE gas.generated_article_id = ga.id "
                    "AND (ga.video_urls IS NULL OR ga.video_urls::text = '[]')"
                )
            )
