"""Repositorio de categorias editoriais."""

from app.db import get_session
from app.models import Category, GeneratedArticle
from sqlalchemy import select


class CategoryRepository:
    """Consultas de categorias do portal."""

    def list_all(self, *, limit: int, offset: int) -> list[Category]:
        """Lista categorias ordenadas por nome."""
        with get_session() as session:
            statement = (
                select(Category)
                .order_by(Category.name.asc())
                .offset(offset)
                .limit(limit)
            )
            return list(session.scalars(statement).all())

    def get_by_id(self, category_id: int) -> Category | None:
        """Busca categoria por id."""
        with get_session() as session:
            statement = select(Category).where(Category.id == category_id)
            return session.scalar(statement)

    def find_by_name(self, name: str) -> Category | None:
        """Busca categoria pelo nome."""
        with get_session() as session:
            statement = select(Category).where(Category.name == name)
            return session.scalar(statement)

    def find_by_slug(self, slug: str) -> Category | None:
        """Busca categoria pelo slug."""
        with get_session() as session:
            statement = select(Category).where(Category.slug == slug)
            return session.scalar(statement)

    def create(self, *, name: str, slug: str) -> Category:
        """Cria uma categoria nova."""
        with get_session() as session:
            category = Category(name=name, slug=slug)
            session.add(category)
            session.commit()
            session.refresh(category)
            return category

    def update(self, *, category_id: int, name: str, slug: str) -> Category | None:
        """Atualiza uma categoria existente."""
        with get_session() as session:
            category = session.get(Category, category_id)
            if category is None:
                return None

            category.name = name
            category.slug = slug
            session.commit()
            session.refresh(category)
            return category

    def delete(self, category_id: int) -> bool:
        """Remove categoria e desassocia artigos vinculados."""
        with get_session() as session:
            category = session.get(Category, category_id)
            if category is None:
                return False

            linked_articles = session.scalars(
                select(GeneratedArticle).where(GeneratedArticle.category_id == category_id)
            ).all()
            for article in linked_articles:
                article.category_id = None

            session.delete(category)
            session.commit()
            return True
