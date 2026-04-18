import json
from dataclasses import dataclass
from typing import Any, List, Optional

import requests

from app.config import settings
from app.models import RawArticle


@dataclass
class GeneratedArticlePayload:
    title: str
    summary: Optional[str]
    body: str
    category: str
    tags: List[str]
    prompt_version: str = "article_v1"


class OllamaClient:
    def generate_article(self, raw_article: RawArticle, prompt_template: str) -> GeneratedArticlePayload:
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
        return (
            f"{prompt_template}\n\n"
            "Responda somente com JSON valido no formato:\n"
            '{"title":"", "summary":"", "body":"", "category":"", "tags":[""]}\n\n'
            f"TITULO ORIGINAL: {raw_article.original_title}\n"
            f"DESCRICAO ORIGINAL: {raw_article.original_description or ''}\n"
            f"AUTOR ORIGINAL: {raw_article.original_author or ''}\n"
            f"URL ORIGINAL: {raw_article.original_url}\n"
            f"CONTEUDO ORIGINAL:\n{raw_article.original_content or ''}\n"
        )

    def _parse_model_response(self, raw_response: str, raw_article: RawArticle) -> dict[str, Any]:
        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError:
            payload = {}

        title = self._as_text(payload.get("title")) or raw_article.original_title
        summary = self._as_optional_text(payload.get("summary")) or raw_article.original_description
        body = self._as_text(payload.get("body")) or (raw_article.original_content or raw_article.original_title)
        category = self._as_text(payload.get("category")) or "geral"
        tags = self._normalize_tags(payload.get("tags"))

        return {
            "title": title,
            "summary": summary,
            "body": body,
            "category": category,
            "tags": tags,
        }

    def _normalize_tags(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [self._as_text(item) for item in value if self._as_text(item)]
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in value.split(",") if part.strip()]
        return []

    def _as_text(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        return ""

    def _as_optional_text(self, value: Any) -> Optional[str]:
        text = self._as_text(value)
        return text or None
