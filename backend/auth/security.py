"""Constantes e helpers de seguranca."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.auth.auth_repository import AuthRepository

# Configuracoes de JWT
DEFAULT_SECRET_KEY = "dev-only-change-me-please-set-jwt-secret-key"
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    DEFAULT_SECRET_KEY,
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = 30

# Esquema de seguranca para o Swagger
security = HTTPBearer(auto_error=False)
_auth_repository = AuthRepository()


def hash_password(password: str) -> str:
    """Gera um hash seguro de senha usando bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha digitada corresponde ao hash armazenado."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um JWT token com informacoes do usuario."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_password_reset_token(*, user_id: int, email: str) -> str:
    """Cria um token temporario para redefinicao de senha."""
    return create_access_token(
        {
            "sub": str(user_id),
            "email": email,
            "purpose": "reset_password",
        },
        expires_delta=timedelta(minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES),
    )


def verify_token(token: str) -> dict | None:
    """Valida um JWT token e retorna os dados se valido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_password_reset_token(token: str) -> dict | None:
    """Valida token de redefinicao de senha e confere o proposito."""
    payload = verify_token(token)
    if payload is None:
        return None
    if payload.get("purpose") != "reset_password":
        return None
    return payload


def get_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extrai o token JWT do header Authorization."""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependencia para validar JWT token e retornar usuario."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token nao fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = _auth_repository.get_by_id(int(user_id))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario do token nao encontrado ou inativo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    }
