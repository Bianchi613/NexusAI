"""Repositorio de autenticacao do portal."""

from Engine.app.db import get_session
from Engine.app.models import User
from sqlalchemy import func, select


class AuthRepository:
    """Consultas de autenticacao relacionadas a usuarios."""

    def find_by_email(self, email: str) -> User | None:
        """Busca usuario pelo email para validar credenciais."""
        normalized_email = email.strip().lower()
        with get_session() as session:
            statement = select(User).where(func.lower(User.email) == normalized_email)
            return session.scalar(statement)

    def get_by_id(self, user_id: int) -> User | None:
        """Busca usuario por id para validacao de token."""
        with get_session() as session:
            statement = select(User).where(User.id == user_id)
            return session.scalar(statement)

    def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: str = "cliente",
    ) -> User:
        """Cria um novo usuario na autenticacao."""
        with get_session() as session:
            user = User(
                name=name,
                email=email,
                password_hash=password_hash,
                role=role,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_active_user(self, email: str) -> User | None:
        """Busca apenas usuarios ativos para login."""
        normalized_email = email.strip().lower()
        with get_session() as session:
            statement = select(User).where(
                (func.lower(User.email) == normalized_email) & User.is_active.is_(True)
            )
            return session.scalar(statement)

    def update_password(self, user_id: int, password_hash: str) -> User | None:
        """Atualiza a senha de um usuario."""
        with get_session() as session:
            user = session.get(User, user_id)
            if user is None:
                return None

            user.password_hash = password_hash
            session.commit()
            session.refresh(user)
            return user
