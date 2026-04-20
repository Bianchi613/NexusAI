"""Repositorio de tags editoriais."""

from app.db import get_session
from app.models import Tag
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

