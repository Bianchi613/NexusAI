"""Rotas agregadas da camada config consumidas pelo frontend."""

from fastapi import APIRouter

from backend.config.config_controller import get_home_controller
from backend.config.config_schema import HomeResponse


router = APIRouter(tags=["Config"])


@router.get("/home", response_model=HomeResponse)
def home_route() -> HomeResponse:
    """Retorna os blocos principais da home."""
    return get_home_controller()
