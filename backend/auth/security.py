"""Constantes e helpers de seguranca."""

import hashlib


AUTH_NOT_IMPLEMENTED_MESSAGE = (
    "A arquitetura de auth ja foi separada, mas a implementacao real "
    "de hash de senha, token e autorizacao ainda sera adicionada."
)


def hash_password(password: str) -> str:
    """Gera um hash simples para persistencia inicial de senha."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
