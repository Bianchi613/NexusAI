"""Repositorio de usuarios do portal."""

from app.db import get_session
from app.models import GeneratedArticle, User
from sqlalchemy import select


class UserRepository:
    """Consultas basicas de usuarios."""

    def find_by_email(self, email: str) -> User | None:
        """Busca usuario pelo email."""
        with get_session() as session:
            statement = select(User).where(User.email == email)
            return session.scalar(statement)

    def get_by_id(self, user_id: int) -> User | None:
        """Busca usuario por id."""
        with get_session() as session:
            statement = select(User).where(User.id == user_id)
            return session.scalar(statement)

    def list_all(self, *, limit: int, offset: int) -> list[User]:
        """Lista usuarios cadastrados."""
        with get_session() as session:
            statement = (
                select(User)
                .order_by(User.id.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(session.scalars(statement).all())

    def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: str,
        is_active: bool,
    ) -> User:
        """Cria um usuario persistido no banco."""
        with get_session() as session:
            user = User(
                name=name,
                email=email,
                password_hash=password_hash,
                role=role,
                is_active=is_active,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def update(self, *, user_id: int, updates: dict[str, object]) -> User | None:
        """Atualiza um usuario existente."""
        with get_session() as session:
            user = session.get(User, user_id)
            if user is None:
                return None

            for field_name, value in updates.items():
                setattr(user, field_name, value)

            session.commit()
            session.refresh(user)
            return user

    def delete(self, user_id: int) -> bool:
        """Remove um usuario e limpa referencias de revisao."""
        with get_session() as session:
            user = session.get(User, user_id)
            if user is None:
                return False

            reviewed_articles = session.scalars(
                select(GeneratedArticle).where(GeneratedArticle.reviewed_by == user_id)
            ).all()
            for article in reviewed_articles:
                article.reviewed_by = None

            session.delete(user)
            session.commit()
            return True
