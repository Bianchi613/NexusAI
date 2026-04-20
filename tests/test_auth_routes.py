"""Testes do fluxo principal de autenticacao."""

from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.auth.auth_repository as auth_repository_module
import backend.auth.auth_service as auth_service_module
import backend.auth.security as security_module
from backend.auth.security import create_access_token
from backend.main import app
from app.models import Base


def _configure_in_memory_auth_db(monkeypatch):
    """Redireciona o auth para um banco SQLite em memoria."""
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

    monkeypatch.setattr(auth_repository_module, "get_session", fake_get_session)
    return SessionLocal


def _configure_auth_status(monkeypatch, *, secret_key: str, expires_minutes: int = 60) -> None:
    """Controla o estado do status operacional do auth durante o teste."""
    monkeypatch.setattr(security_module, "SECRET_KEY", secret_key)
    monkeypatch.setattr(auth_service_module, "SECRET_KEY", secret_key)
    monkeypatch.setattr(auth_service_module, "ACCESS_TOKEN_EXPIRE_MINUTES", expires_minutes)


def test_auth_status_returns_503_when_secret_is_default(monkeypatch) -> None:
    """Status publico deve indicar degradacao quando o secret ainda e o padrao."""
    _configure_auth_status(
        monkeypatch,
        secret_key=security_module.DEFAULT_SECRET_KEY,
    )
    client = TestClient(app)

    response = client.get("/api/v1/auth/status")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["ready"] is False
    assert response.json()["checks"]["jwt_secret_not_default"] is False


def test_auth_status_returns_200_when_secret_is_ready(monkeypatch) -> None:
    """Status publico deve retornar pronto com uma configuracao minima valida."""
    _configure_auth_status(
        monkeypatch,
        secret_key="super-secret-key-with-32-plus-characters-12345",
    )
    client = TestClient(app)

    response = client.get("/api/v1/auth/status")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["ready"] is True
    assert all(response.json()["checks"].values()) is True


def test_auth_me_returns_401_without_token(monkeypatch) -> None:
    """Rotas protegidas devem responder 401 quando faltar token."""
    _configure_in_memory_auth_db(monkeypatch)
    client = TestClient(app)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Token nao fornecido."}


def test_auth_register_normalizes_email_and_login_is_case_insensitive(monkeypatch) -> None:
    """Cadastro e login devem tratar e-mail sem depender da capitalizacao."""
    _configure_in_memory_auth_db(monkeypatch)
    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Auth.User@Example.com",
            "name": "  Auth User  ",
            "password": "Senha@123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "auth.user@example.com"
    assert response.json()["name"] == "Auth User"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "AUTH.USER@EXAMPLE.COM", "password": "Senha@123"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "auth.user@example.com"


def test_auth_rejects_token_for_missing_user(monkeypatch) -> None:
    """Token com usuario inexistente nao deve ser aceito."""
    _configure_in_memory_auth_db(monkeypatch)
    client = TestClient(app)
    token = create_access_token(
        {"sub": "999", "email": "ghost@example.com", "role": "cliente"}
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Usuario do token nao encontrado ou inativo."
    }
