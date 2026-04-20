"""Repositorio de leitura e revisao de artigos."""

from datetime import datetime, timezone

from app.db import get_session
from app.models import GeneratedArticle
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class ArticleRepository:
    """Consulta artigos aproveitando os modelos do projeto."""

    def list_published(self, *, limit: int, offset: int) -> list[GeneratedArticle]:
        """Lista artigos publicados para a vitrine publica."""
        with get_session() as session:
            statement = (
                select(GeneratedArticle)
                .options(selectinload(GeneratedArticle.category))
                .where(GeneratedArticle.status == "publicada")
                .order_by(GeneratedArticle.published_at.desc(), GeneratedArticle.id.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(session.scalars(statement).all())

    def get_published_by_id(self, article_id: int) -> GeneratedArticle | None:
        """Busca um unico artigo publicado por id."""
        with get_session() as session:
            statement = (
                select(GeneratedArticle)
                .options(selectinload(GeneratedArticle.category))
                .where(
                    GeneratedArticle.id == article_id,
                    GeneratedArticle.status == "publicada",
                )
            )
            return session.scalar(statement)

    def list_pending_review(self, *, limit: int, offset: int) -> list[GeneratedArticle]:
        """Lista artigos aguardando revisao editorial."""
        with get_session() as session:
            statement = (
                select(GeneratedArticle)
                .options(selectinload(GeneratedArticle.category))
                .where(GeneratedArticle.status == "nao_revisada")
                .order_by(GeneratedArticle.created_at.desc(), GeneratedArticle.id.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(session.scalars(statement).all())

    def get_by_id(self, article_id: int) -> GeneratedArticle | None:
        """Busca artigo por id sem filtrar status."""
        with get_session() as session:
            statement = (
                select(GeneratedArticle)
                .options(selectinload(GeneratedArticle.category))
                .where(GeneratedArticle.id == article_id)
            )
            return session.scalar(statement)

    def mark_as_reviewed(self, *, article_id: int, reviewer_id: int, status: str) -> GeneratedArticle | None:
        """Atualiza o estado editorial de um artigo."""
        with get_session() as session:
            article = session.get(GeneratedArticle, article_id)
            if article is None:
                return None

            now = datetime.now(timezone.utc)
            article.status = status
            article.reviewed_by = reviewer_id
            article.reviewed_at = now
            article.published_at = now if status == "publicada" else None
            session.commit()
            session.refresh(article)
            return article

