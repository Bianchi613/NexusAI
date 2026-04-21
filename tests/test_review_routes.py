"""Testes das rotas de revisao editorial."""

from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.articles.article_repository as article_repository_module
import backend.categories.category_repository as category_repository_module
import backend.tags.tag_repository as tag_repository_module
import backend.users.user_repository as user_repository_module
from backend.main import app
from app.models import Base, Category, GeneratedArticle, Tag, User


def _configure_in_memory_review_db(monkeypatch):
    """Redireciona os repositorios da camada de revisao para SQLite em memoria."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    @contextmanager
    def fake_get_session():
        with SessionLocal() as session:
            yield session

    monkeypatch.setattr(article_repository_module, "get_session", fake_get_session)
    monkeypatch.setattr(category_repository_module, "get_session", fake_get_session)
    monkeypatch.setattr(tag_repository_module, "get_session", fake_get_session)
    monkeypatch.setattr(user_repository_module, "get_session", fake_get_session)
    return SessionLocal


def test_reviewer_can_manage_articles_categories_and_tags(monkeypatch) -> None:
    """Revisor deve conseguir operar os recursos editoriais centrais."""
    session_factory = _configure_in_memory_review_db(monkeypatch)

    with session_factory() as session:
        category = Category(name="Tecnologia", slug="tecnologia")
        tag = Tag(name="IA", slug="ia")
        reviewer = User(
            name="Revisor Portal",
            email="revisor@example.com",
            password_hash="hash",
            role="revisor",
            is_active=True,
        )
        session.add_all([category, tag, reviewer])
        session.flush()

        article = GeneratedArticle(
            title="Rascunho inicial",
            summary="Resumo inicial",
            body="Corpo inicial",
            category_id=category.id,
            status="nao_revisada",
            tags=[tag.id],
            image_urls=[],
            video_urls=[],
        )
        session.add(article)
        session.commit()
        session.refresh(article)
        reviewer_id = reviewer.id
        category_id = category.id
        tag_id = tag.id
        article_id = article.id

    client = TestClient(app)

    list_response = client.get(f"/api/v1/review/articles?reviewer_id={reviewer_id}")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_article_response = client.put(
        f"/api/v1/review/articles/{article_id}?reviewer_id={reviewer_id}",
        json={
            "title": "Materia revisada",
            "body": "Corpo revisado",
            "status": "publicada",
            "category_id": category_id,
            "tag_ids": [tag_id],
        },
    )
    assert update_article_response.status_code == 200
    updated_article = update_article_response.json()
    assert updated_article["title"] == "Materia revisada"
    assert updated_article["status"] == "publicada"
    assert updated_article["reviewed_by"] == reviewer_id

    create_category_response = client.post(
        f"/api/v1/review/categories?reviewer_id={reviewer_id}",
        json={"name": "Clima", "slug": "clima"},
    )
    assert create_category_response.status_code == 200
    created_category = create_category_response.json()
    assert created_category["slug"] == "clima"

    update_category_response = client.put(
        f"/api/v1/review/categories/{created_category['id']}?reviewer_id={reviewer_id}",
        json={"name": "Clima Atualizado"},
    )
    assert update_category_response.status_code == 200
    assert update_category_response.json()["name"] == "Clima Atualizado"

    create_tag_response = client.post(
        f"/api/v1/review/tags?reviewer_id={reviewer_id}",
        json={"name": "Pesquisa", "slug": "pesquisa"},
    )
    assert create_tag_response.status_code == 200
    created_tag = create_tag_response.json()
    assert created_tag["slug"] == "pesquisa"

    update_tag_response = client.put(
        f"/api/v1/review/tags/{created_tag['id']}?reviewer_id={reviewer_id}",
        json={"name": "Pesquisa Atualizada"},
    )
    assert update_tag_response.status_code == 200
    assert update_tag_response.json()["name"] == "Pesquisa Atualizada"

    delete_tag_response = client.delete(f"/api/v1/review/tags/{created_tag['id']}?reviewer_id={reviewer_id}")
    assert delete_tag_response.status_code == 200

    delete_category_response = client.delete(
        f"/api/v1/review/categories/{created_category['id']}?reviewer_id={reviewer_id}"
    )
    assert delete_category_response.status_code == 200

    delete_article_response = client.delete(f"/api/v1/review/articles/{article_id}?reviewer_id={reviewer_id}")
    assert delete_article_response.status_code == 200


def test_non_reviewer_cannot_use_review_panel(monkeypatch) -> None:
    """Usuario comum nao deve conseguir operar a camada de revisao."""
    session_factory = _configure_in_memory_review_db(monkeypatch)

    with session_factory() as session:
        client_user = User(
            name="Cliente",
            email="cliente@example.com",
            password_hash="hash",
            role="cliente",
            is_active=True,
        )
        session.add(client_user)
        session.commit()
        session.refresh(client_user)
        client_user_id = client_user.id

    client = TestClient(app)
    response = client.get(f"/api/v1/review/articles?reviewer_id={client_user_id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "O usuario informado nao possui permissao de revisor."
