"""Schemas de tags."""

from pydantic import BaseModel, Field, ConfigDict


class TagCreateRequest(BaseModel):
    """Payload de criacao de tag."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Argentina",
                "slug": "argentina"
            }
        }
    )

    name: str = Field(min_length=1, max_length=100, example="Argentina")
    slug: str | None = Field(default=None, min_length=1, max_length=120, example="argentina")


class TagUpdateRequest(BaseModel):
    """Payload de atualizacao parcial de tag."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Amazon Brasil",
                "slug": "amazon-brasil"
            }
        }
    )

    name: str | None = Field(default=None, min_length=1, max_length=100, example="Amazon Brasil")
    slug: str | None = Field(default=None, min_length=1, max_length=120, example="amazon-brasil")


class TagResponse(BaseModel):
    """Representacao publica de tag."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 58,
                "name": "Argentina",
                "slug": "argentina"
            }
        }
    )

    id: int = Field(example=58)
    name: str = Field(example="Argentina")
    slug: str = Field(example="argentina")