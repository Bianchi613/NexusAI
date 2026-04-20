"""Schemas de categorias."""

from pydantic import BaseModel, Field, ConfigDict


class CategoryCreateRequest(BaseModel):
    """Payload de criacao de categoria."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Categoria Exemplo",
                "slug": "categoria-exemplo"
            }
        }
    )

    name: str = Field(
        min_length=1,
        max_length=100,
        example="Categoria Exemplo"
    )
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        example="categoria-exemplo"
    )


class CategoryUpdateRequest(BaseModel):
    """Payload de atualizacao parcial de categoria."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Outra Categoria",
                "slug": "outra-categoria"
            }
        }
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        example="Outra Categoria"
    )
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        example="outra-categoria"
    )


class CategoryResponse(BaseModel):
    """Representacao publica de categoria."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 0,
                "name": "Categoria Exemplo",
                "slug": "categoria-exemplo"
            }
        }
    )

    id: int = Field(example=0)
    name: str = Field(example="Categoria Exemplo")
    slug: str = Field(example="categoria-exemplo")