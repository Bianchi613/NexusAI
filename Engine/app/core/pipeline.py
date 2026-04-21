"""Orquestracao principal do pipeline de noticias.

Este modulo coordena o fluxo inteiro:
- coleta de fontes API, RSS e JSON Feed
- deduplicacao do lote bruto
- comparacao do bruto com `raw_articles`
- selecao dos candidatos para geracao
- chamada da IA
- persistencia da materia final e de falhas de processamento
"""

from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from typing import List

import requests

from Engine.app.ai.agentic import AgenticOllamaClient
from Engine.app.ai.gemini import GeneratedArticlePayload, GeminiClient
from Engine.app.ai.ollama import OllamaClient
from Engine.app.collectors.json_feed import JSONFeedCollector
from Engine.app.collectors.news_api import NewsAPICollector
from Engine.app.collectors.rss import RSSCollector
from Engine.app.config import settings
from Engine.app.core.article_filters import (
    are_titles_similar,
    build_fallback_tags,
    guess_category_from_article,
    normalize_label,
    normalize_title,
    normalize_url,
    slugify,
)
from Engine.app.db import get_session
from Engine.app.models import Category, GeneratedArticle, GeneratedArticleSource, NewsSource, ProcessingFailure, RawArticle, Tag
from sqlalchemy import func, select


class NewsPipeline:
    """Orquestra uma rodada completa de coleta, selecao e geracao."""

    def __init__(self) -> None:
        self.api_collector = NewsAPICollector()
        self.rss_collector = RSSCollector()
        self.json_feed_collector = JSONFeedCollector()
        self.ai_provider = self._resolve_ai_provider()
        self.ai_client = self._build_ai_client()
        self.prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "article.txt"

    def _resolve_ai_provider(self) -> str:
        """Normaliza o provider configurado e aplica fallback seguro."""
        provider = (settings.ai_provider or "gemini").strip().lower()
        aliases = {
            "agentic": "agentic_ollama",
            "agentic_ollama": "agentic_ollama",
            "gemini": "gemini",
            "ollama": "ollama",
        }
        return aliases.get(provider, "gemini")

    def _build_ai_client(self):
        """Cria o cliente de IA ativo da rodada atual."""
        if self.ai_provider == "agentic_ollama":
            return AgenticOllamaClient(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url,
                timeout_seconds=settings.ollama_timeout_seconds,
            )
        if self.ai_provider == "ollama":
            return OllamaClient()
        return GeminiClient()

    def _get_active_ai_model(self) -> str:
        """Explica qual modelo deve ser salvo no artigo gerado."""
        if self.ai_provider in {"ollama", "agentic_ollama"}:
            return settings.ollama_model
        return settings.gemini_model

    def _get_generation_failure_stage(self) -> str:
        """Padroniza o nome da etapa de falha conforme o provider."""
        if self.ai_provider == "agentic_ollama":
            return "agentic_ollama_generate"
        if self.ai_provider == "ollama":
            return "ollama_generate"
        return "gemini_generate"

    def _safe_print(self, message: str) -> None:
        """Evita que logs quebrem por caracteres fora do encoding do console."""
        encoding = sys.stdout.encoding or "utf-8"
        safe_message = message.encode(encoding, errors="backslashreplace").decode(encoding)
        print(safe_message)

    def load_prompt(self) -> str:
        """Carrega o prompt textual usado pela camada de IA."""
        if not self.prompt_path.exists():
            return ""
        return self.prompt_path.read_text(encoding="utf-8")

    def run(self) -> List[GeneratedArticle]:
        """Executa uma rodada completa do pipeline."""
        prompt_template = self.load_prompt()
        target_limit = settings.pipeline_max_items_per_run
        if settings.pipeline_test_mode:
            target_limit = min(target_limit, max(1, settings.pipeline_test_max_items))

        with get_session() as session:
            collected_articles = []
            collected_articles.extend(self.api_collector.collect(session))
            collected_articles.extend(self.rss_collector.collect(session))
            collected_articles.extend(self.json_feed_collector.collect(session))
            # Primeiro removemos duplicidade dentro do lote coletado; so depois
            # limitamos variedade por fonte e persistimos no banco.
            collected_articles = self._deduplicate_batch(collected_articles)
            collected_articles = self._limit_varied_articles_per_source(collected_articles)
            stored_articles = self._persist_raw_articles(session, collected_articles)
            session.commit()
            generation_candidates = self._prepare_generation_candidates(session, stored_articles, target_limit)
            return self._generate_articles_for_run(session, generation_candidates, prompt_template, target_limit)

    def _persist_raw_article(self, session, article: RawArticle) -> RawArticle:
        """Atalho de teste/uso interno para persistir um unico bruto."""
        return self._persist_raw_articles(session, [article])[0]

    def _persist_raw_articles(self, session, articles: List[RawArticle]) -> List[RawArticle]:
        """Salva artigos brutos comparando apenas contra `raw_articles`.

        Regras principais:
        - URL continua sendo comparada globalmente
        - titulo normalizado e `content_hash` usam a janela de lookback
        """
        if not articles:
            return []

        lookback_start = datetime.now(timezone.utc) - timedelta(days=settings.deduplication_lookback_days)
        article_urls = {normalize_url(article.original_url) for article in articles if normalize_url(article.original_url)}
        existing_by_url: dict[str, RawArticle] = {}

        if article_urls:
            existing_urls = session.scalars(select(RawArticle).where(RawArticle.original_url.in_(article_urls))).all()
            existing_by_url = {normalize_url(article.original_url): article for article in existing_urls}

        recent_articles = session.scalars(select(RawArticle).where(RawArticle.collected_at >= lookback_start)).all()
        existing_by_hash: dict[str, RawArticle] = {}
        existing_by_title: dict[str, RawArticle] = {}

        for existing_article in recent_articles:
            if existing_article.content_hash and existing_article.content_hash not in existing_by_hash:
                existing_by_hash[existing_article.content_hash] = existing_article

            normalized_existing_title = normalize_title(existing_article.original_title)
            if normalized_existing_title and normalized_existing_title not in existing_by_title:
                existing_by_title[normalized_existing_title] = existing_article

        persisted_articles: List[RawArticle] = []
        for article in articles:
            article_url = normalize_url(article.original_url)
            article_title = normalize_title(article.original_title)

            existing_article = None
            if article_url:
                existing_article = existing_by_url.get(article_url)
            if existing_article is None and article.content_hash:
                existing_article = existing_by_hash.get(article.content_hash)
            if existing_article is None and article_title:
                existing_article = existing_by_title.get(article_title)

            if existing_article is not None:
                persisted_articles.append(existing_article)
                continue

            session.add(article)
            session.flush()
            persisted_articles.append(article)

            if article_url:
                existing_by_url[article_url] = article
            if article.content_hash:
                existing_by_hash[article.content_hash] = article
            if article_title:
                existing_by_title[article_title] = article

        return persisted_articles

    def _already_generated(self, session, raw_article_id: int) -> bool:
        """Verifica se uma `raw_article` ja foi usada em geracao anterior."""
        existing = session.scalar(
            select(GeneratedArticleSource).where(GeneratedArticleSource.raw_article_id == raw_article_id)
        )
        return existing is not None

    def _get_or_create_category(self, session, name: str) -> Category:
        """Resolve ou cria a categoria editorial de uma materia gerada."""
        normalized_name = self._normalize_category_name(name)
        slug = slugify(normalized_name)
        category = session.scalar(select(Category).where(Category.slug == slug))
        if category is not None:
            return category

        category = Category(name=normalized_name, slug=slug)
        session.add(category)
        session.flush()
        return category

    def _get_or_create_tag_ids(self, session, tag_names: List[str]) -> List[int]:
        """Resolve ou cria tags e devolve apenas seus ids."""
        tag_ids: List[int] = []
        seen_slugs: set[str] = set()

        for name in tag_names[: settings.max_tags_per_article]:
            normalized_name = normalize_label(name)
            if not normalized_name:
                continue

            slug = slugify(normalized_name)
            if slug in seen_slugs:
                continue

            seen_slugs.add(slug)
            tag = session.scalar(select(Tag).where(Tag.slug == slug))
            if tag is None:
                tag = Tag(name=normalized_name, slug=slug)
                session.add(tag)
                session.flush()

            tag_ids.append(tag.id)

        return tag_ids

    def _resolve_tag_names(
        self,
        payload: GeneratedArticlePayload,
        raw_article: RawArticle,
        source_name: str | None,
    ) -> List[str]:
        """Combina tags da IA com fallback local para nunca deixar a materia vazia."""
        resolved_tags: List[str] = []
        seen_slugs: set[str] = set()

        def append_tag(name: str) -> None:
            normalized_name = normalize_label(name)
            if not normalized_name:
                return

            slug = slugify(normalized_name)
            if not slug or slug in seen_slugs:
                return

            seen_slugs.add(slug)
            resolved_tags.append(normalized_name)

        for tag_name in payload.tags:
            append_tag(tag_name)

        fallback_tags = build_fallback_tags(
            title=payload.title or raw_article.original_title,
            summary=payload.summary or raw_article.original_description,
            category=payload.category,
            source_name=source_name,
            max_tags=settings.max_tags_per_article,
        )
        for tag_name in fallback_tags:
            if len(resolved_tags) >= settings.max_tags_per_article:
                break
            append_tag(tag_name)

        return resolved_tags[: settings.max_tags_per_article]

    def _normalize_category_name(self, name: str) -> str:
        """Normaliza categoria gerada e limita ao conjunto permitido."""
        normalized_name = normalize_label(name or "Geral") or "Geral"
        allowed_by_slug = {slugify(category): category for category in settings.allowed_categories}
        return allowed_by_slug.get(slugify(normalized_name), "Geral")

    def _deduplicate_batch(self, articles: List[RawArticle]) -> List[RawArticle]:
        """Remove duplicidade obvia dentro do lote ainda em memoria."""
        unique_articles: List[RawArticle] = []
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()
        seen_hashes: set[str] = set()

        for article in articles:
            normalized_url = normalize_url(article.original_url)
            normalized_title = normalize_title(article.original_title)
            content_hash = article.content_hash or ""

            if normalized_url and normalized_url in seen_urls:
                continue
            if normalized_title and normalized_title in seen_titles:
                continue
            if content_hash and content_hash in seen_hashes:
                continue

            if normalized_url:
                seen_urls.add(normalized_url)
            if normalized_title:
                seen_titles.add(normalized_title)
            if content_hash:
                seen_hashes.add(content_hash)

            unique_articles.append(article)

        return unique_articles

    def _limit_varied_articles_per_source(self, articles: List[RawArticle]) -> List[RawArticle]:
        """Mantem apenas uma quantidade limitada de itens por fonte."""
        max_per_source = settings.max_raw_articles_per_source
        if max_per_source <= 0:
            return articles

        selected_articles: List[RawArticle] = []
        selected_by_source: dict[int | None, List[RawArticle]] = {}

        for article in articles:
            source_key = article.source_id
            source_articles = selected_by_source.setdefault(source_key, [])
            if len(source_articles) >= max_per_source:
                continue

            source_articles.append(article)
            selected_articles.append(article)

        return selected_articles

    def _select_articles_for_run(self, session, articles: List[RawArticle], limit: int) -> List[RawArticle]:
        """Seleciona candidatos equilibrando tipo de fonte e rotacao."""
        if limit <= 0:
            return articles

        source_type_by_id = {
            source_id: source_type
            for source_id, source_type in session.execute(
                select(NewsSource.id, NewsSource.source_type).where(
                    NewsSource.id.in_({article.source_id for article in articles})
                )
            ).all()
        }
        by_type_and_source: dict[str, dict[int, List[RawArticle]]] = {}
        type_order: List[str] = []
        source_order_by_type: dict[str, List[int]] = {}

        for article in articles:
            source_type = source_type_by_id.get(article.source_id, "rss")
            if source_type not in by_type_and_source:
                by_type_and_source[source_type] = {}
                source_order_by_type[source_type] = []
                type_order.append(source_type)

            if article.source_id not in by_type_and_source[source_type]:
                by_type_and_source[source_type][article.source_id] = []
                source_order_by_type[source_type].append(article.source_id)

            by_type_and_source[source_type][article.source_id].append(article)

        if not type_order:
            return []

        generated_count = session.scalar(select(func.count()).select_from(GeneratedArticle)) or 0
        type_rotation = generated_count % len(type_order)
        rotated_type_order = type_order[type_rotation:] + type_order[:type_rotation]
        rotated_source_order_by_type = {
            source_type: self._rotate_items(source_ids, generated_count)
            for source_type, source_ids in source_order_by_type.items()
        }

        selected: List[RawArticle] = []
        source_counts: Counter[int] = Counter()
        while len(selected) < limit:
            added_in_pass = False
            for source_type in rotated_type_order:
                next_article = self._pop_next_article_for_type(
                    by_type_and_source[source_type],
                    rotated_source_order_by_type[source_type],
                )
                if next_article is None:
                    continue
                if source_counts[next_article.source_id] >= settings.max_articles_per_source_per_run:
                    continue

                selected.append(next_article)
                source_counts[next_article.source_id] += 1
                added_in_pass = True
                if len(selected) >= limit:
                    return selected

            if not added_in_pass:
                break

        return selected

    def _pop_next_article_for_type(
        self,
        by_source: dict[int, List[RawArticle]],
        source_order: List[int],
    ) -> RawArticle | None:
        """Faz round-robin entre fontes de um mesmo tipo."""
        if not source_order:
            return None

        for _ in range(len(source_order)):
            source_id = source_order.pop(0)
            articles = by_source.get(source_id, [])
            if not articles:
                continue

            article = articles.pop(0)
            if articles:
                source_order.append(source_id)
            else:
                by_source.pop(source_id, None)

            return article

        return None

    def _rotate_items(self, items: List[int] | List[str], rotation_seed: int) -> List[int] | List[str]:
        """Rotaciona a ordem base para evitar sempre o mesmo primeiro item."""
        if not items:
            return []

        rotation = rotation_seed % len(items)
        return list(items[rotation:] + items[:rotation])

    def _get_candidate_limit(self, total_articles: int, target_limit: int) -> int:
        """Calcula o tamanho do pool antes da geracao final."""
        if total_articles <= 0:
            return 0
        if target_limit <= 0:
            return total_articles

        multiplier = max(1, settings.pipeline_candidate_pool_multiplier)
        buffer = max(0, settings.pipeline_generation_buffer)
        return min(total_articles, max(target_limit, target_limit * multiplier + buffer))

    def _prepare_generation_candidates(
        self,
        session,
        stored_articles: List[RawArticle],
        target_limit: int,
    ) -> List[RawArticle]:
        """Aplica os filtros finais antes de chamar a IA."""
        candidates = self._exclude_already_generated_articles(session, stored_articles)
        candidate_limit = self._get_candidate_limit(len(candidates), target_limit)
        if candidate_limit > 0:
            candidates = self._select_articles_for_run(session, candidates, candidate_limit)
        candidates = self._exclude_similar_articles_in_batch(candidates)
        return self._prioritize_articles_for_generation(session, candidates)

    def _exclude_already_generated_articles(self, session, articles: List[RawArticle]) -> List[RawArticle]:
        """Remove brutos que ja viraram materia em execucoes anteriores."""
        if not articles:
            return []

        raw_article_ids = [article.id for article in articles if article is not None and article.id is not None]
        if not raw_article_ids:
            return []

        generated_ids = {
            raw_article_id
            for (raw_article_id,) in session.execute(
                select(GeneratedArticleSource.raw_article_id).where(GeneratedArticleSource.raw_article_id.in_(raw_article_ids))
            ).all()
        }
        return [article for article in articles if article is not None and article.id not in generated_ids]

    def _exclude_similar_articles_in_batch(self, articles: List[RawArticle]) -> List[RawArticle]:
        """Evita quase-duplicatas dentro do lote atual de geracao."""
        if not articles:
            return []

        filtered_articles: List[RawArticle] = []
        seen_hashes: set[str] = set()
        seen_titles: list[str] = []

        for article in articles:
            if article.content_hash and article.content_hash in seen_hashes:
                continue

            if any(are_titles_similar(article.original_title, seen_title) for seen_title in seen_titles):
                continue

            filtered_articles.append(article)
            if article.content_hash:
                seen_hashes.add(article.content_hash)
            if article.original_title:
                seen_titles.append(article.original_title)

        return filtered_articles

    def _prioritize_articles_for_generation(self, session, articles: List[RawArticle]) -> List[RawArticle]:
        """Intercala categorias previstas para aumentar variedade editorial."""
        if len(articles) <= 1:
            return articles

        source_name_by_id = {
            source_id: source_name
            for source_id, source_name in session.execute(
                select(NewsSource.id, NewsSource.name).where(NewsSource.id.in_({article.source_id for article in articles}))
            ).all()
        }

        grouped_by_category: dict[str, List[RawArticle]] = {}
        category_order: List[str] = []
        for article in articles:
            predicted_category = guess_category_from_article(
                article.original_title,
                article.original_description,
                source_name=source_name_by_id.get(article.source_id),
            )
            if predicted_category not in grouped_by_category:
                grouped_by_category[predicted_category] = []
                category_order.append(predicted_category)
            grouped_by_category[predicted_category].append(article)

        prioritized_articles: List[RawArticle] = []
        while len(prioritized_articles) < len(articles):
            added_in_pass = False
            for category_name in category_order:
                if not grouped_by_category[category_name]:
                    continue
                prioritized_articles.append(grouped_by_category[category_name].pop(0))
                added_in_pass = True

            if not added_in_pass:
                break

        return prioritized_articles

    def _generate_articles_for_run(
        self,
        session,
        stored_articles: List[RawArticle],
        prompt_template: str,
        target_limit: int,
    ) -> List[GeneratedArticle]:
        """Gera materias finais e registra falhas sem abortar a rodada inteira."""
        generated_articles: List[GeneratedArticle] = []
        effective_limit = target_limit if target_limit > 0 else len(stored_articles)
        raw_article_ids = [article.id for article in stored_articles if article is not None]

        for raw_article_id in raw_article_ids:
            if len(generated_articles) >= effective_limit:
                break
            raw_article = session.get(RawArticle, raw_article_id)
            if raw_article is None or self._already_generated(session, raw_article.id):
                continue

            try:
                payload = self.ai_client.generate_article(raw_article, prompt_template)
                generated_article = self._store_generated_article(session, raw_article, payload)
                generated_articles.append(generated_article)
            except requests.RequestException as exc:
                session.rollback()
                self._log_processing_failure(session, raw_article, self._get_generation_failure_stage(), exc)
                self._safe_print(
                    "Falha ao gerar materia para "
                    f"'{raw_article.original_title}' ({raw_article.original_url}): "
                    f"{exc.__class__.__name__}: {exc}"
                )
            except Exception as exc:
                session.rollback()
                self._log_processing_failure(session, raw_article, "pipeline_process", exc)
                self._safe_print(
                    "Erro inesperado ao processar "
                    f"'{raw_article.original_title}' ({raw_article.original_url}): "
                    f"{exc.__class__.__name__}: {exc}"
                )

        return generated_articles

    def _store_generated_article(
        self,
        session,
        raw_article: RawArticle,
        payload: GeneratedArticlePayload,
    ) -> GeneratedArticle:
        """Persiste a materia final e cria o vinculo com a noticia bruta."""
        category = self._get_or_create_category(session, payload.category)
        source = session.get(NewsSource, raw_article.source_id) if raw_article.source_id is not None else None
        resolved_tag_names = self._resolve_tag_names(payload, raw_article, source.name if source else None)
        tag_ids = self._get_or_create_tag_ids(session, resolved_tag_names)

        generated_article = GeneratedArticle(
            title=payload.title,
            summary=payload.summary,
            body=payload.body,
            category_id=category.id if category else None,
            status="nao_revisada",
            ai_model=self._get_active_ai_model(),
            prompt_version=payload.prompt_version,
            tags=tag_ids,
            image_urls=list(raw_article.original_image_urls or []),
            video_urls=list(raw_article.original_video_urls or []),
        )
        session.add(generated_article)
        session.flush()

        session.add(
            GeneratedArticleSource(
                generated_article_id=generated_article.id,
                raw_article_id=raw_article.id,
            )
        )
        session.commit()
        session.refresh(generated_article)
        return generated_article

    def _log_processing_failure(self, session, raw_article: RawArticle, stage: str, exc: Exception) -> None:
        """Registra erro processual no banco sem explodir a execucao toda."""
        try:
            failure = ProcessingFailure(
                source_id=raw_article.source_id,
                raw_article_id=raw_article.id,
                stage=stage,
                error_type=exc.__class__.__name__,
                message=str(exc),
                article_title=raw_article.original_title,
                article_url=raw_article.original_url,
            )
            session.add(failure)
            session.commit()
        except Exception:
            session.rollback()
