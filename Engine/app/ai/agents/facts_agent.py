"""Agente responsavel pela extracao factual da materia."""

from __future__ import annotations

from typing import Any

from Engine.app.ai.agentic import BaseAgent, FactSheet
from Engine.app.core.article_filters import build_source_body, build_source_summary
from Engine.app.models import RawArticle


class FactsAgent(BaseAgent):
    """Consolida fatos verificaveis e limites da fonte."""

    def run(self, *, raw_article: RawArticle) -> FactSheet:
        prompt = self._build_prompt(raw_article)
        payload = self.request_json(prompt)
        return self._to_fact_sheet(payload, raw_article)

    def _build_prompt(self, raw_article: RawArticle) -> str:
        source_summary = build_source_summary(raw_article.original_description, raw_article.original_content, limit=600)
        source_body = build_source_body(raw_article.original_content, raw_article.original_description, limit=2400)

        return (
            f"{self.load_prompt()}\n\n"
            f"TITULO ORIGINAL: {raw_article.original_title}\n"
            f"URL ORIGINAL: {raw_article.original_url}\n"
            f"AUTOR ORIGINAL: {raw_article.original_author or ''}\n"
            f"RESUMO DA FONTE:\n{source_summary}\n\n"
            f"CONTEUDO DA FONTE:\n{source_body}\n"
        )

    def _to_fact_sheet(self, payload: dict[str, Any], raw_article: RawArticle) -> FactSheet:
        fallback_event = raw_article.original_title.strip() or "Fato principal nao informado"
        return FactSheet(
            main_event=self._as_text(payload.get("main_event")) or fallback_event,
            key_points=self._as_list(payload.get("key_points")),
            entities=self._as_list(payload.get("entities")),
            dates=self._as_list(payload.get("dates")),
            numbers=self._as_list(payload.get("numbers")),
            source_limits=self._as_list(payload.get("source_limits")),
            factual_notes=self._as_list(payload.get("factual_notes")),
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
