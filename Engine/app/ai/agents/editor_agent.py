"""Agente editor que faz a revisao final do rascunho."""

from __future__ import annotations

from typing import Any

from Engine.app.ai.agentic import ArticleOutline, BaseAgent, DraftArticle, FactSheet
from Engine.app.ai.ollama import GeneratedArticlePayload
from Engine.app.core.article_filters import normalize_generated_title, sanitize_article_text, truncate_text
from Engine.app.models import RawArticle


class EditorAgent(BaseAgent):
    """Refina o rascunho e devolve o payload final esperado pelo pipeline."""

    def run(
        self,
        *,
        raw_article: RawArticle,
        fact_sheet: FactSheet,
        outline: ArticleOutline,
        draft: DraftArticle,
        prompt_template: str = "",
    ) -> GeneratedArticlePayload:
        prompt = self._build_prompt(
            raw_article=raw_article,
            fact_sheet=fact_sheet,
            outline=outline,
            draft=draft,
            prompt_template=prompt_template,
        )
        payload = self.request_json(prompt)
        return self._to_payload(payload, raw_article=raw_article, outline=outline, draft=draft)

    def _build_prompt(
        self,
        *,
        raw_article: RawArticle,
        fact_sheet: FactSheet,
        outline: ArticleOutline,
        draft: DraftArticle,
        prompt_template: str,
    ) -> str:
        return (
            f"{self.load_prompt()}\n\n"
            f"TITULO ORIGINAL: {raw_article.original_title}\n"
            f"FICHA FACTUAL ENXUTA:\n{self.dump_json(self._compact_fact_sheet(fact_sheet))}\n\n"
            f"OUTLINE EDITORIAL ENXUTO:\n{self.dump_json(self._compact_outline(outline))}\n\n"
            f"RASCUNHO DO REDATOR ENXUTO:\n{self.dump_json(self._compact_draft(draft))}\n"
        )

    def _to_payload(
        self,
        payload: dict[str, Any],
        *,
        raw_article: RawArticle,
        outline: ArticleOutline,
        draft: DraftArticle,
    ) -> GeneratedArticlePayload:
        title = self._as_text(payload.get("title")) or draft.title or outline.title or raw_article.original_title
        summary = self._as_text(payload.get("summary")) or draft.summary or outline.summary
        body = self._as_text(payload.get("body")) or draft.body
        category = self._as_text(payload.get("category")) or draft.category or outline.category or "Geral"
        tags = self._as_list(payload.get("tags")) or draft.tags or outline.tags

        cleaned_title = normalize_generated_title(title, raw_article.original_title)
        cleaned_summary = truncate_text(summary, 420) if summary else None
        cleaned_body = truncate_text(sanitize_article_text(body), 4200)

        return GeneratedArticlePayload(
            title=cleaned_title,
            summary=cleaned_summary,
            body=cleaned_body,
            category=category,
            tags=tags,
            prompt_version="agentic_ollama_v1",
        )

    def _compact_fact_sheet(self, fact_sheet: FactSheet) -> dict[str, Any]:
        """Entrega apenas os fatos mais importantes para a revisao final."""
        return {
            "main_event": fact_sheet.main_event,
            "key_points": fact_sheet.key_points[:4],
            "entities": fact_sheet.entities[:4],
            "source_limits": fact_sheet.source_limits[:2],
        }

    def _compact_outline(self, outline: ArticleOutline) -> dict[str, Any]:
        """Reduz o outline ao necessario para a etapa editorial final."""
        return {
            "angle": outline.angle,
            "title": outline.title,
            "summary": outline.summary,
            "section_order": outline.section_order[:4],
            "category": outline.category,
            "tags": outline.tags[:5],
        }

    def _compact_draft(self, draft: DraftArticle) -> dict[str, Any]:
        """Evita enviar um rascunho grande demais para a etapa de revisao."""
        return {
            "title": draft.title,
            "summary": draft.summary,
            "body": truncate_text(draft.body, 1800),
            "category": draft.category,
            "tags": draft.tags[:5],
            "editor_notes": draft.editor_notes[:3],
        }

    @staticmethod
    def _as_text(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    @classmethod
    def _as_list(cls, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        items = [cls._as_text(item) for item in value]
        return [item for item in items if item]
