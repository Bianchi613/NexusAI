"""Repositorio de tags editoriais."""

from app.db import get_session
from app.models import GeneratedArticle, Tag
from sqlalchemy import select


class TagRepository:
    """Consultas de tags do portal."""

    def list_all(self, *, limit: int, offset: int) -> list[Tag]:
        """Lista tags ordenadas por nome."""
        with get_session() as session:
            statement = (
                select(Tag)
                .order_by(Tag.name.asc())
                .offset(offset)
                .limit(limit)
            )
            return list(session.scalars(statement).all())

    def get_by_id(self, tag_id: int) -> Tag | None:
        """Busca tag por id."""
        with get_session() as session:
            statement = select(Tag).where(Tag.id == tag_id)
            return session.scalar(statement)

    def find_by_name(self, name: str) -> Tag | None:
        """Busca tag pelo nome."""
        with get_session() as session:
            statement = select(Tag).where(Tag.name == name)
            return session.scalar(statement)

    def find_by_slug(self, slug: str) -> Tag | None:
        """Busca tag pelo slug."""
        with get_session() as session:
            statement = select(Tag).where(Tag.slug == slug)
            return session.scalar(statement)

    def create(self, *, name: str, slug: str) -> Tag:
        """Cria uma tag nova."""
        with get_session() as session:
            tag = Tag(name=name, slug=slug)
            session.add(tag)
            session.commit()
            session.refresh(tag)
            return tag

    def update(self, *, tag_id: int, name: str, slug: str) -> Tag | None:
        """Atualiza uma tag existente."""
        with get_session() as session:
            tag = session.get(Tag, tag_id)
            if tag is None:
                return None

            tag.name = name
            tag.slug = slug
            session.commit()
            session.refresh(tag)
            return tag

    def delete(self, tag_id: int) -> bool:
        """Remove tag e limpa referencias em artigos."""
        with get_session() as session:
            tag = session.get(Tag, tag_id)
            if tag is None:
                return False

            articles = session.scalars(select(GeneratedArticle)).all()
            for article in articles:
                current_tags = list(article.tags or [])
                filtered_tags = [current_tag for current_tag in current_tags if current_tag != tag_id]
                if filtered_tags != current_tags:
                    article.tags = filtered_tags

            session.delete(tag)
            session.commit()
            return True
