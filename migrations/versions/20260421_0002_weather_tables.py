"""Add weather tables

Revision ID: 20260421_0002
Revises: 20260418_0001
Create Date: 2026-04-21 18:20:00

Esta migration cria as tabelas de suporte ao modulo de clima:
- snapshots de previsao por localidade
- alertas meteorologicos normalizados
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260421_0002"
down_revision = "20260418_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria as tabelas persistentes do modulo de clima."""
    op.create_table(
        "weather_forecast_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("location_key", sa.String(length=80), nullable=False),
        sa.Column("city_name", sa.String(length=120), nullable=False),
        sa.Column("state_code", sa.String(length=2), nullable=False),
        sa.Column("state_name", sa.String(length=80), nullable=True),
        sa.Column("source_name", sa.String(length=40), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("headline", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("daily_forecast", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("advisory_items", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("extra_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("location_key", name="uq_weather_forecast_snapshots_location_key"),
    )

    op.create_table(
        "weather_alerts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("source_name", sa.String(length=40), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=30), nullable=False, server_default=sa.text("'informativo'")),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'ativo'")),
        sa.Column("area", sa.Text(), nullable=True),
        sa.Column("areas", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("external_id", name="uq_weather_alerts_external_id"),
    )


def downgrade() -> None:
    """Remove as tabelas do modulo de clima."""
    op.drop_table("weather_alerts")
    op.drop_table("weather_forecast_snapshots")
