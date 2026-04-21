"""Agente encarregado de redigir a materia."""

from __future__ import annotations

from typing import Any

from Engine.app.ai.agentic import ArticleOutline, BaseAgent, DraftArticle, FactSheet
from Engine.app.core.article_filters import truncate_text
from Engine.app.models import RawArticle


class WriterAgent(BaseAgent):
    """Escreve o rascunho final com base nos fatos e no outline."""

    def run(
        self,
        *,
        raw_article: RawArticle,
        fact_sheet: FactSheet,
        outline: ArticleOutline,
        prompt_template: str = "",
    ) -> DraftArticle:
        prompt = self._build_prompt(
            raw_article=raw_article,
            fact_sheet=fact_sheet,
            outline=outline,
            prompt_template=prompt_template,
        )
        payload = self.request_json(prompt)
        return self._to_draft(payload, outline)

    def _build_prompt(
        self,
        *,
        raw_article: RawArticle,
        fact_sheet: FactSheet,
        outline: ArticleOutline,
        prompt_template: str,
    ) -> str:
        return (
            f"{self.load_prompt()}\n\n"
            f"TITULO ORIGINAL: {raw_article.original_title}\n"
            f"FICHA FACTUAL ENXUTA:\n{self.dump_json(self._compact_fact_sheet(fact_sheet))}\n\n"
            f"OUTLINE EDITORIAL ENXUTO:\n{self.dump_json(self._compact_outline(outline))}\n"
        )

    def _to_draft(self, payload: dict[str, Any], outline: ArticleOutline) -> DraftArticle:
        fallback_title = outline.title or "Materia sem titulo"
        fallback_summary = outline.summary or None
        return DraftArticle(
            title=self._as_text(payload.get("title")) or fallback_title,
            summary=self._as_text(payload.get("summary")) or fallback_summary,
            body=self._as_text(payload.get("body")),
            category=self._as_text(payload.get("category")) or outline.category or "Geral",
            tags=self._as_list(payload.get("tags")) or list(outline.tags),
            editor_notes=self._as_list(payload.get("editor_notes")),
        )

    def _compact_fact_sheet(self, fact_sheet: FactSheet) -> dict[str, Any]:
        """Entrega apenas os fatos mais relevantes para a redacao."""
        return {
            "main_event": fact_sheet.main_event,
            "key_points": fact_sheet.key_points[:5],
            "entities": fact_sheet.entities[:4],
            "dates": fact_sheet.dates[:3],
            "numbers": fact_sheet.numbers[:3],
        }

    def _compact_outline(self, outline: ArticleOutline) -> dict[str, Any]:
        """Mantem so o outline necessario para escrever o rascunho."""
        return {
            "angle": outline.angle,
            "title": outline.title,
            "summary": outline.summary,
            "section_order": outline.section_order[:4],
            "paragraph_goals": [truncate_text(goal, 120) for goal in outline.paragraph_goals[:4]],
            "category": outline.category,
            "tags": outline.tags[:5],
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
