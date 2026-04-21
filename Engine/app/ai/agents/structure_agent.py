"""Agente que define o enquadramento editorial da materia."""

from __future__ import annotations

from typing import Any

from Engine.app.ai.agentic import ArticleOutline, BaseAgent, FactSheet
from Engine.app.models import RawArticle


class StructureAgent(BaseAgent):
    """Traduz os fatos em uma estrutura jornalistica reutilizavel."""

    def run(self, *, raw_article: RawArticle, fact_sheet: FactSheet, prompt_template: str = "") -> ArticleOutline:
        prompt = self._build_prompt(raw_article=raw_article, fact_sheet=fact_sheet, prompt_template=prompt_template)
        payload = self.request_json(prompt)
        return self._to_outline(payload, raw_article)

    def _build_prompt(self, *, raw_article: RawArticle, fact_sheet: FactSheet, prompt_template: str) -> str:
        return (
            f"{self.load_prompt()}\n\n"
            f"DIRETRIZ GERAL DO PROJETO:\n{prompt_template.strip()}\n\n"
            f"TITULO ORIGINAL: {raw_article.original_title}\n"
            f"FICHA FACTUAL:\n{self.dump_json(fact_sheet.__dict__)}\n"
        )

    def _to_outline(self, payload: dict[str, Any], raw_article: RawArticle) -> ArticleOutline:
        fallback_title = raw_article.original_title.strip() or "Materia sem titulo"
        return ArticleOutline(
            angle=self._as_text(payload.get("angle")) or "Abordagem factual e clara",
            title=self._as_text(payload.get("title")) or fallback_title,
            summary=self._as_text(payload.get("summary")),
            section_order=self._as_list(payload.get("section_order")),
            paragraph_goals=self._as_list(payload.get("paragraph_goals")),
            category=self._as_text(payload.get("category")) or "Geral",
            tags=self._as_list(payload.get("tags")),
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
