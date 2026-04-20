"""Repositorio de usuarios do portal."""

from app.db import get_session
from app.models import User
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

