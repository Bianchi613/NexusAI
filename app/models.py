from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('cliente', 'revisor')", name="ck_users_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="cliente")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    reviewed_articles: Mapped[List["GeneratedArticle"]] = relationship(back_populates="reviewer")


class NewsSource(Base):
    __tablename__ = "news_sources"
    __table_args__ = (
        CheckConstraint("source_type IN ('api', 'rss', 'json_feed')", name="ck_news_sources_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    raw_articles: Mapped[List["RawArticle"]] = relationship(back_populates="source")
    processing_failures: Mapped[List["ProcessingFailure"]] = relationship(back_populates="source")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    generated_articles: Mapped[List["GeneratedArticle"]] = relationship(back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class RawArticle(Base):
    __tablename__ = "raw_articles"
    __table_args__ = (
        UniqueConstraint("original_url", name="uq_raw_articles_original_url"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("news_sources.id"), nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255))
    original_title: Mapped[str] = mapped_column(Text, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    original_description: Mapped[Optional[str]] = mapped_column(Text)
    original_content: Mapped[Optional[str]] = mapped_column(Text)
    original_author: Mapped[Optional[str]] = mapped_column(String(255))
    original_image_url: Mapped[Optional[str]] = mapped_column(Text)
    original_image_urls: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), nullable=False, default=list)
    original_video_urls: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), nullable=False, default=list)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    content_hash: Mapped[Optional[str]] = mapped_column(String(255))

    source: Mapped["NewsSource"] = relationship(back_populates="raw_articles")
    generated_links: Mapped[List["GeneratedArticleSource"]] = relationship(back_populates="raw_article")
    processing_failures: Mapped[List["ProcessingFailure"]] = relationship(back_populates="raw_article")


class GeneratedArticle(Base):
    __tablename__ = "generated_articles"
    __table_args__ = (
        CheckConstraint(
            "status IN ('nao_revisada', 'publicada', 'rejeitada')",
            name="ck_generated_articles_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="nao_revisada")
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50))
    tags: Mapped[List[int]] = mapped_column(MutableList.as_mutable(JSON), nullable=False, default=list)
    image_urls: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), nullable=False, default=list)
    video_urls: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    category: Mapped[Optional["Category"]] = relationship(back_populates="generated_articles")
    reviewer: Mapped[Optional["User"]] = relationship(back_populates="reviewed_articles")
    raw_article_links: Mapped[List["GeneratedArticleSource"]] = relationship(back_populates="generated_article")

    @property
    def source_ids(self) -> List[int]:
        return [link.raw_article_id for link in self.raw_article_links]


class GeneratedArticleSource(Base):
    __tablename__ = "generated_article_sources"
    __table_args__ = (
        UniqueConstraint(
            "generated_article_id",
            "raw_article_id",
            name="uq_generated_article_sources_pair",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    generated_article_id: Mapped[int] = mapped_column(ForeignKey("generated_articles.id"), nullable=False)
    raw_article_id: Mapped[int] = mapped_column(ForeignKey("raw_articles.id"), nullable=False)

    generated_article: Mapped["GeneratedArticle"] = relationship(back_populates="raw_article_links")
    raw_article: Mapped["RawArticle"] = relationship(back_populates="generated_links")


class ProcessingFailure(Base):
    __tablename__ = "processing_failures"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("news_sources.id"))
    raw_article_id: Mapped[Optional[int]] = mapped_column(ForeignKey("raw_articles.id"))
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    error_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    article_title: Mapped[Optional[str]] = mapped_column(Text)
    article_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    source: Mapped[Optional["NewsSource"]] = relationship(back_populates="processing_failures")
    raw_article: Mapped[Optional["RawArticle"]] = relationship(back_populates="processing_failures")
