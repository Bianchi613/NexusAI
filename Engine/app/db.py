"""Camada central de conexao com o banco.

Este arquivo concentra:
- criacao do engine SQLAlchemy
- fabrica de sessoes usada pelo restante do projeto
- utilitarios pequenos para expor a URL ativa

O controle de schema nao fica mais aqui. A estrutura do banco e versionada
via Alembic, por isso `init_db()` existe apenas como ponto de compatibilidade.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from Engine.app.config import settings


engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_database_url() -> str:
    """Retorna a URL de banco ja normalizada pela configuracao."""
    return settings.database_url


def get_session() -> Session:
    """Cria uma nova sessao SQLAlchemy para uma unidade de trabalho."""
    return SessionLocal()


def init_db() -> None:
    """Mantido por compatibilidade; schema e gerenciado via Alembic."""
    return None
