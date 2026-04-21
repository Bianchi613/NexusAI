"""Controller das rotas agregadas da camada config."""

from backend.config.config_schema import HomeResponse
from backend.config.config_service import get_home


def get_home_controller() -> HomeResponse:
    """Retorna os blocos principais da home."""
    return get_home()
