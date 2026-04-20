"""Repositorio de categorias editoriais."""

from app.db import get_session
from app.models import Category
from sqlalchemy import select


class CategoryRepository:
    """Consultas de categorias do portal."""

    def list_all(self) -> list[Category]:
        """Lista categorias ordenadas por nome."""
        with get_session() as session:
            statement = select(Category).order_by(Category.name.asc())
            return list(session.scalars(statement).all())

