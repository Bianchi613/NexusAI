"""Ponto de entrada da API do portal.

Este modulo expoe apenas a aplicacao ASGI `app`.
A execucao local deve ser feita pela CLI do FastAPI:

- `fastapi dev` para desenvolvimento
- `fastapi run` para execucao sem reload
"""

from fastapi import APIRouter, FastAPI

from backend.articles.article_routes import router as article_router
from backend.auth.auth_routes import router as auth_router
from backend.categories.category_routes import router as category_router
from backend.config.settings import settings
from backend.review.review_routes import router as review_router
from backend.tags.tag_routes import router as tag_router
from backend.users.user_routes import router as user_router


def create_app() -> FastAPI:
    """Cria a aplicacao FastAPI do portal."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    api_router = APIRouter()
    api_router.include_router(auth_router)
    api_router.include_router(user_router)
    api_router.include_router(article_router)
    api_router.include_router(category_router)
    api_router.include_router(tag_router)
    api_router.include_router(review_router)

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
