"""Cliente da camada de IA usada para gerar a materia final.

Este modulo:
- recebe uma `RawArticle`
- monta um prompt estruturado
- chama o Ollama local
- valida e higieniza a resposta retornada pelo modelo

O objetivo aqui nao e decidir fluxo de negocio. O foco e transformar uma
resposta do modelo em um payload seguro para persistencia.
"""

import json
from dataclasses import dataclass
from typing import Any, List, Optional

import requests

from app.config import settings
from app.core.article_filters import (
    build_source_body,
    build_source_summary,
    is_suspicious_generated_text,
    normalize_generated_title,
    sanitize_article_text,
    truncate_text,
)
from app.models import RawArticle


@dataclass
class GeneratedArticlePayload:
    """Representa a estrutura minima esperada da resposta da IA."""

    title: str
    summary: Optional[str]
    body: str
    category: str
    tags: List[str]
    prompt_version: str = "article_v1"


class OllamaClient:
    """Cliente HTTP enxuto para comunicacao com o Ollama local."""

    def generate_article(self, raw_article: RawArticle, prompt_template: str) -> GeneratedArticlePayload:
        """Gera uma materia estruturada a partir de uma noticia bruta."""
        prompt = self._build_prompt(raw_article, prompt_template)

        response = requests.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=settings.ollama_timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        structured = self._parse_model_response(payload.get("response", "{}"), raw_article)

        return GeneratedArticlePayload(
            title=structured["title"],
            summary=structured.get("summary"),
            body=structured["body"],
            category=structured.get("category") or "geral",
            tags=structured.get("tags") or [],
        )

    def _build_prompt(self, raw_article: RawArticle, prompt_template: str) -> str:
        """Consolida prompt base e contexto da materia original."""
        source_description = build_source_summary(raw_article.original_description, raw_article.original_content, limit=500)
        source_content = build_source_body(raw_article.original_content, raw_article.original_description, limit=2500)
        return (
            f"{prompt_template}\n\n"
            "Responda somente com JSON valido no formato:\n"
            '{"title":"", "summary":"", "body":"", "category":"", "tags":[""]}\n\n'
            f"TITULO ORIGINAL: {raw_article.original_title}\n"
            f"DESCRICAO ORIGINAL: {source_description}\n"
            f"AUTOR ORIGINAL: {raw_article.original_author or ''}\n"
            f"URL ORIGINAL: {raw_article.original_url}\n"
            f"CONTEUDO ORIGINAL:\n{source_content}\n"
        )

    def _parse_model_response(self, raw_response: str, raw_article: RawArticle) -> dict[str, Any]:
        """Faz parsing defensivo e aplica fallbacks quando a IA falha."""
        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError:
            payload = {}

        fallback_summary = build_source_summary(raw_article.original_description, raw_article.original_content)
        fallback_body = build_source_body(raw_article.original_content, raw_article.original_description)

        title = self._as_text(payload.get("title")) or raw_article.original_title
        summary = self._as_optional_text(payload.get("summary")) or fallback_summary
        body = self._as_text(payload.get("body")) or fallback_body
        category = self._as_text(payload.get("category")) or "geral"
        tags = self._normalize_tags(payload.get("tags"))

        cleaned_title = normalize_generated_title(title, raw_article.original_title)
        cleaned_summary = self._sanitize_optional_text(summary)
        cleaned_body = sanitize_article_text(body)

        if is_suspicious_generated_text(cleaned_summary, min_length=40):
            cleaned_summary = fallback_summary or None

        if is_suspicious_generated_text(cleaned_body, min_length=80):
            cleaned_body = fallback_body

        cleaned_summary = truncate_text(cleaned_summary, 320) if cleaned_summary else None
        cleaned_body = truncate_text(cleaned_body, 2000)

        return {
            "title": cleaned_title,
            "summary": cleaned_summary,
            "body": cleaned_body,
            "category": category,
            "tags": tags,
        }

    def _normalize_tags(self, value: Any) -> List[str]:
        """Aceita tags como lista ou string separada por virgulas."""
        if isinstance(value, list):
            return [self._as_text(item) for item in value if self._as_text(item)]
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in value.split(",") if part.strip()]
        return []

    def _as_text(self, value: Any) -> str:
        """Converte valores soltos em string limpa."""
        if isinstance(value, str):
            return value.strip()
        return ""

    def _as_optional_text(self, value: Any) -> Optional[str]:
        """Retorna `None` quando nao houver texto util."""
        text = self._as_text(value)
        return text or None

    def _sanitize_optional_text(self, value: Optional[str]) -> Optional[str]:
        """Aplica a mesma sanitizacao do pipeline para campos opcionais."""
        text = sanitize_article_text(value)
        return text or None
