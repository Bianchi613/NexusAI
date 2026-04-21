"""Agente encarregado de redigir a materia."""

from __future__ import annotations

from typing import Any

from Engine.app.ai.agentic import ArticleOutline, BaseAgent, DraftArticle, FactSheet
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
            f"DIRETRIZ GERAL DO PROJETO:\n{prompt_template.strip()}\n\n"
            f"TITULO ORIGINAL: {raw_article.original_title}\n"
            f"FICHA FACTUAL:\n{self.dump_json(fact_sheet.__dict__)}\n\n"
            f"OUTLINE EDITORIAL:\n{self.dump_json(outline.__dict__)}\n"
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

    @staticmethod
    def _as_text(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    @classmethod
    def _as_list(cls, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        items = [cls._as_text(item) for item in value]
        return [item for item in items if item]
