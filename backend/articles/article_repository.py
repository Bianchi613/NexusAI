"""Repositorio de leitura e revisao de artigos."""

from datetime import datetime, timezone

from app.db import get_session
from app.models import Category, GeneratedArticle, GeneratedArticleSource, RawArticle, Tag, User
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class ArticleRepository:
    """Consulta artigos aproveitando os modelos do projeto."""

    @staticmethod
    def _list_options():
        """Opcoes comuns para listagem."""
        return (
            selectinload(GeneratedArticle.category),
            selectinload(GeneratedArticle.raw_article_links),
        )

    @staticmethod
    def _detail_options():
        """Opcoes comuns para detalhes."""
        return (
            selectinload(GeneratedArticle.category),
            selectinload(GeneratedArticle.reviewer),
            selectinload(GeneratedArticle.raw_article_links),
        )

    def list_all(
        self,
        *,
        limit: int,
        offset: int,
        status: str | None = None,
        category_id: int | None = None,
        reviewed_by: int | None = None,
    ) -> list[GeneratedArticle]:
        """Lista artigos com filtros opcionais."""
        with get_session() as session:
            statement = (
                select(GeneratedArticle)
                .options(*self._list_options())
                .order_by(GeneratedArticle.created_at.desc(), GeneratedArticle.id.desc())
                .offset(offset)
                .limit(limit)
            )
            if status is not None:
                statement = statement.where(GeneratedArticle.status == status)
            if category_id is not None:
                statement = statement.where(GeneratedArticle.category_id == category_id)
            if reviewed_by is not None:
                statement = statement.where(GeneratedArticle.reviewed_by == reviewed_by)
            return list(session.scalars(statement).all())

    def list_published(self, *, limit: int, offset: int) -> list[GeneratedArticle]:
        """Lista artigos publicados para a vitrine publica."""
        return self.list_all(limit=limit, offset=offset, status="publicada")

    def get_published_by_id(self, article_id: int) -> GeneratedArticle | None:
        """Busca um unico artigo publicado por id."""
        with get_session() as session:
            statement = (
                select(GeneratedArticle)
                .options(*self._detail_options())
                .where(
                    GeneratedArticle.id == article_id,
                    GeneratedArticle.status == "publicada",
                )
            )
            return session.scalar(statement)

    def list_pending_review(self, *, limit: int, offset: int) -> list[GeneratedArticle]:
        """Lista artigos aguardando revisao editorial."""
        return self.list_all(limit=limit, offset=offset, status="nao_revisada")

    def get_by_id(self, article_id: int) -> GeneratedArticle | None:
        """Busca artigo por id sem filtrar status."""
        with get_session() as session:
            statement = (
                select(GeneratedArticle)
                .options(*self._detail_options())
                .where(GeneratedArticle.id == article_id)
            )
            return session.scalar(statement)

    def create(self, *, article_data: dict[str, object], source_ids: list[int]) -> GeneratedArticle:
        """Cria um artigo e seus vinculos com noticias brutas."""
        with get_session() as session:
            article = GeneratedArticle(**article_data)
            session.add(article)
            session.flush()

            for raw_article_id in source_ids:
                session.add(
                    GeneratedArticleSource(
                        generated_article_id=article.id,
                        raw_article_id=raw_article_id,
                    )
                )

            session.commit()

            statement = (
                select(GeneratedArticle)
                .options(*self._detail_options())
                .where(GeneratedArticle.id == article.id)
            )
            return session.scalar(statement)

    def update(
        self,
        *,
        article_id: int,
        article_data: dict[str, object],
        source_ids: list[int] | None,
    ) -> GeneratedArticle | None:
        """Atualiza um artigo existente."""
        with get_session() as session:
            article = session.get(GeneratedArticle, article_id)
            if article is None:
                return None

            for field_name, value in article_data.items():
                setattr(article, field_name, value)

            if source_ids is not None:
                existing_links = session.scalars(
                    select(GeneratedArticleSource).where(
                        GeneratedArticleSource.generated_article_id == article_id
                    )
                ).all()
                for link in existing_links:
                    session.delete(link)
                session.flush()

                for raw_article_id in source_ids:
                    session.add(
                        GeneratedArticleSource(
                            generated_article_id=article_id,
                            raw_article_id=raw_article_id,
                        )
                    )

            session.commit()

            statement = (
                select(GeneratedArticle)
                .options(*self._detail_options())
                .where(GeneratedArticle.id == article_id)
            )
            return session.scalar(statement)

    def delete(self, article_id: int) -> bool:
        """Remove um artigo e seus vinculos de origem."""
        with get_session() as session:
            article = session.get(GeneratedArticle, article_id)
            if article is None:
                return False

            existing_links = session.scalars(
                select(GeneratedArticleSource).where(
                    GeneratedArticleSource.generated_article_id == article_id
                )
            ).all()
            for link in existing_links:
                session.delete(link)

            session.delete(article)
            session.commit()
            return True

    def category_exists(self, category_id: int) -> bool:
        """Valida existencia de categoria."""
        with get_session() as session:
            return session.get(Category, category_id) is not None

    def existing_tag_ids(self, tag_ids: list[int]) -> set[int]:
        """Retorna conjunto de tags existentes."""
        if not tag_ids:
            return set()
        with get_session() as session:
            statement = select(Tag.id).where(Tag.id.in_(tag_ids))
            return set(session.scalars(statement).all())

    def existing_raw_article_ids(self, raw_article_ids: list[int]) -> set[int]:
        """Retorna conjunto de raw articles existentes."""
        if not raw_article_ids:
            return set()
        with get_session() as session:
            statement = select(RawArticle.id).where(RawArticle.id.in_(raw_article_ids))
            return set(session.scalars(statement).all())

    def get_reviewer(self, reviewer_id: int) -> User | None:
        """Busca usuario revisor por id."""
        with get_session() as session:
            statement = select(User).where(User.id == reviewer_id)
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

            statement = (
                select(GeneratedArticle)
                .options(*self._detail_options())
                .where(GeneratedArticle.id == article_id)
            )
            return session.scalar(statement)
