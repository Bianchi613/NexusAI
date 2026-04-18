"""Initial schema

Revision ID: 20260418_0001
Revises: None
Create Date: 2026-04-18 11:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260418_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.UniqueConstraint("name", name="uq_categories_name"),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )

    op.create_table(
        "news_sources",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("source_type IN ('api', 'rss', 'json_feed')", name="ck_news_sources_type"),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.UniqueConstraint("name", name="uq_tags_name"),
        sa.UniqueConstraint("slug", name="uq_tags_slug"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default=sa.text("'cliente'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('cliente', 'revisor')", name="ck_users_role"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "raw_articles",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("original_title", sa.Text(), nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("original_description", sa.Text(), nullable=True),
        sa.Column("original_content", sa.Text(), nullable=True),
        sa.Column("original_author", sa.String(length=255), nullable=True),
        sa.Column("original_image_url", sa.Text(), nullable=True),
        sa.Column("original_image_urls", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("original_video_urls", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("content_hash", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["news_sources.id"]),
        sa.UniqueConstraint("original_url", name="uq_raw_articles_original_url"),
    )

    op.create_table(
        "generated_articles",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'nao_revisada'")),
        sa.Column("ai_model", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=50), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("image_urls", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("video_urls", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "status IN ('nao_revisada', 'publicada', 'rejeitada')",
            name="ck_generated_articles_status",
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"]),
    )

    op.create_table(
        "processing_failures",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("raw_article_id", sa.Integer(), nullable=True),
        sa.Column("stage", sa.String(length=50), nullable=False),
        sa.Column("error_type", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("article_title", sa.Text(), nullable=True),
        sa.Column("article_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["raw_article_id"], ["raw_articles.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["news_sources.id"]),
    )

    op.create_table(
        "generated_article_sources",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("generated_article_id", sa.Integer(), nullable=False),
        sa.Column("raw_article_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["generated_article_id"], ["generated_articles.id"]),
        sa.ForeignKeyConstraint(["raw_article_id"], ["raw_articles.id"]),
        sa.UniqueConstraint(
            "generated_article_id",
            "raw_article_id",
            name="uq_generated_article_sources_pair",
        ),
    )


def downgrade() -> None:
    op.drop_table("generated_article_sources")
    op.drop_table("processing_failures")
    op.drop_table("generated_articles")
    op.drop_table("raw_articles")
    op.drop_table("users")
    op.drop_table("tags")
    op.drop_table("news_sources")
    op.drop_table("categories")
