"""Testes das rotas de leitura consumidas pelo frontend."""

from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.articles.article_repository as article_repository_module
import backend.categories.category_repository as category_repository_module
import backend.tags.tag_repository as tag_repository_module
from backend.main import app
from Engine.app.models import Base, Category, GeneratedArticle, Tag, User


def _configure_in_memory_read_db(monkeypatch):
    """Redireciona os repositorios de leitura para SQLite em memoria."""
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
    return SessionLocal


def test_category_and_article_read_routes_only_expose_published_articles(monkeypatch) -> None:
    """O frontend deve receber apenas artigos com status publicada."""
    session_factory = _configure_in_memory_read_db(monkeypatch)

    with session_factory() as session:
        categoria_geral = Category(name="Geral", slug="geral")
        categoria_ciencia = Category(name="Ciencia", slug="ciencia")
        tag = Tag(name="Pesquisa", slug="pesquisa")
        reviewer = User(
            name="Revisor Portal",
            email="revisor@example.com",
            password_hash="hash",
            role="revisor",
            is_active=True,
        )
        session.add_all([categoria_geral, categoria_ciencia, tag, reviewer])
        session.flush()

        artigo_geral = GeneratedArticle(
            title="Plantao acompanha os principais desdobramentos do dia",
            summary="Resumo da editoria principal",
            body="Primeiro paragrafo.\n\nSegundo paragrafo com mais contexto.",
            category_id=categoria_geral.id,
            status="publicada",
            tags=[tag.id],
            image_urls=["https://example.com/image.jpg"],
            video_urls=[],
            reviewed_by=reviewer.id,
        )
        artigo_ciencia = GeneratedArticle(
            title="Laboratorios ampliam parcerias para compartilhar dados",
            summary="Resumo do artigo publico",
            body="Primeiro paragrafo.\n\nSegundo paragrafo com mais contexto.",
            category_id=categoria_ciencia.id,
            status="publicada",
            tags=[tag.id],
            image_urls=["https://example.com/ciencia.jpg"],
            video_urls=[],
            reviewed_by=reviewer.id,
        )
        artigo_rascunho = GeneratedArticle(
            title="Artigo nao publicado",
            summary="Nao deve aparecer",
            body="Corpo do rascunho",
            category_id=categoria_ciencia.id,
            status="nao_revisada",
            tags=[],
            image_urls=[],
            video_urls=[],
        )
        article_rejeitado = GeneratedArticle(
            title="Artigo rejeitado",
            summary="Tambem nao deve aparecer",
            body="Corpo rejeitado",
            category_id=categoria_ciencia.id,
            status="rejeitada",
            tags=[],
            image_urls=[],
            video_urls=[],
            reviewed_by=reviewer.id,
        )
        session.add_all([artigo_geral, artigo_ciencia, artigo_rascunho, article_rejeitado])
        session.commit()
        session.refresh(artigo_geral)
        session.refresh(artigo_ciencia)

    client = TestClient(app)

    categories_response = client.get("/api/v1/categories")

    assert categories_response.status_code == 200
    categories = categories_response.json()
    assert [item["slug"] for item in categories] == ["noticias", "ciencia"]
    assert categories[0]["name"] == "Noticias"

    category_response = client.get("/api/v1/categories/noticias/articles")

    assert category_response.status_code == 200
    category_payload = category_response.json()
    assert len(category_payload["items"]) == 1
    assert category_payload["items"][0]["title"] == "Plantao acompanha os principais desdobramentos do dia"

    detail_category_response = client.get("/api/v1/categories/ciencia")

    assert detail_category_response.status_code == 200
    category_detail = detail_category_response.json()
    assert category_detail["category"]["slug"] == "ciencia"
    assert len(category_detail["articles"]) == 1
    assert category_detail["featured_article"]["title"] == "Laboratorios ampliam parcerias para compartilhar dados"

    published_response = client.get("/api/v1/articles/published")

    assert published_response.status_code == 200
    published = published_response.json()
    assert len(published["items"]) == 2
    assert {item["title"] for item in published["items"]} == {
        "Plantao acompanha os principais desdobramentos do dia",
        "Laboratorios ampliam parcerias para compartilhar dados",
    }

    article_slug = next(item["slug"] for item in published["items"] if item["title"] == artigo_ciencia.title)
    detail_response = client.get(f"/api/v1/articles/slug/{article_slug}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["title"] == "Laboratorios ampliam parcerias para compartilhar dados"
    assert detail["author"] == "Revisor Portal"
    assert detail["tags"][0]["name"] == "Pesquisa"
    assert len(detail["body_paragraphs"]) == 2

    related_response = client.get(f"/api/v1/articles/slug/{article_slug}/related")

    assert related_response.status_code == 200
    assert related_response.json() == []

    home_response = client.get("/api/v1/home")

    assert home_response.status_code == 200
    home_payload = home_response.json()
    assert len(home_payload["latest_articles"]) == 2
    assert len(home_payload["watch_articles"]) == 0
    assert [item["title"] for item in home_payload["latest_articles"]] == [
        "Laboratorios ampliam parcerias para compartilhar dados",
        "Plantao acompanha os principais desdobramentos do dia",
    ]
    assert [item["category"]["slug"] for item in home_payload["featured_categories"]] == ["noticias", "ciencia"]


def test_invalid_virtual_slug_returns_404(monkeypatch) -> None:
    """Slug sem id valido nao deve resolver artigo publicado."""
    _configure_in_memory_read_db(monkeypatch)
    client = TestClient(app)

    response = client.get("/api/v1/articles/slug/slug-invalido")

    assert response.status_code == 404
    assert response.json() == {"detail": "Artigo publicado nao encontrado."}


def test_home_watch_articles_prioritize_articles_with_image_by_category(monkeypatch) -> None:
    """A home deve preferir uma materia com imagem por editoria na faixa inferior."""
    session_factory = _configure_in_memory_read_db(monkeypatch)

    with session_factory() as session:
        categoria_geral = Category(name="Geral", slug="geral")
        categoria_politica = Category(name="Politica", slug="politica")
        categoria_tecnologia = Category(name="Tecnologia", slug="tecnologia")
        categoria_ciencia = Category(name="Ciencia", slug="ciencia")
        session.add_all([categoria_geral, categoria_politica, categoria_tecnologia, categoria_ciencia])
        session.flush()

        latest_articles = [
            GeneratedArticle(
                title=f"Ultima geral {index}",
                summary="Resumo geral",
                body="Corpo da materia geral.",
                category_id=categoria_geral.id,
                status="publicada",
                tags=[],
                image_urls=[f"https://example.com/geral-{index}.jpg"],
                video_urls=[],
            )
            for index in range(6)
        ]

        politica_sem_imagem = GeneratedArticle(
            title="Politica sem imagem",
            summary="Resumo da politica sem imagem",
            body="Corpo da materia sem imagem.",
            category_id=categoria_politica.id,
            status="publicada",
            tags=[],
            image_urls=[],
            video_urls=[],
        )
        politica_com_imagem = GeneratedArticle(
            title="Politica com imagem",
            summary="Resumo da politica com imagem",
            body="Corpo da materia com imagem.",
            category_id=categoria_politica.id,
            status="publicada",
            tags=[],
            image_urls=["https://example.com/politica.jpg"],
            video_urls=[],
        )
        tecnologia_com_imagem = GeneratedArticle(
            title="Tecnologia com imagem",
            summary="Resumo de tecnologia",
            body="Corpo da materia de tecnologia.",
            category_id=categoria_tecnologia.id,
            status="publicada",
            tags=[],
            image_urls=["https://example.com/tecnologia.jpg"],
            video_urls=[],
        )
        ciencia_com_imagem = GeneratedArticle(
            title="Ciencia com imagem",
            summary="Resumo de ciencia",
            body="Corpo da materia de ciencia.",
            category_id=categoria_ciencia.id,
            status="publicada",
            tags=[],
            image_urls=["https://example.com/ciencia.jpg"],
            video_urls=[],
        )

        session.add_all(
            [
                politica_sem_imagem,
                politica_com_imagem,
                tecnologia_com_imagem,
                ciencia_com_imagem,
                *latest_articles,
            ]
        )
        session.commit()

    client = TestClient(app)

    home_response = client.get("/api/v1/home")

    assert home_response.status_code == 200
    home_payload = home_response.json()
    watch_titles = [item["title"] for item in home_payload["watch_articles"]]

    assert "Politica com imagem" in watch_titles
    assert "Politica sem imagem" not in watch_titles
