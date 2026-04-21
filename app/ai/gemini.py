from dataclasses import dataclass
from typing import Any, List, Optional
import json

from google import genai

from app.config import settings
from app.core.article_filters import (
    build_source_body,
    build_source_summary,
    is_probably_english_text,
    is_suspicious_generated_text,
    normalize_generated_title,
    remove_structured_noise,
    repair_text_encoding,
    sanitize_article_text,
    truncate_text,
)
from app.models import RawArticle


@dataclass
class GeneratedArticlePayload:
    title: str
    summary: Optional[str]
    body: str
    category: str
    tags: List[str]
    prompt_version: str = "article_v2"


@dataclass
class GenerationPlan:
    source_summary_limit: int
    source_body_limit: int
    fallback_body_limit: int
    target_body_min: int
    target_body_max: int
    paragraph_range: str
    prompt_version: str = "article_v2"


class GeminiClient:
    """Cliente da Gemini API para gerar matéria estruturada."""

    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model or "gemini-2.0-flash"

    def generate_article(self, raw_article: RawArticle, prompt_template: str) -> GeneratedArticlePayload:
        plan = self._build_generation_plan(raw_article)
        prompt = self._build_prompt(raw_article, prompt_template, plan)
        structured = self._request_and_parse(prompt, raw_article, plan)

        retry_reason = self._get_retry_reason(structured, raw_article, plan)
        if retry_reason is not None:
            retry_prompt = self._build_retry_prompt(
                raw_article,
                prompt_template,
                structured,
                plan,
                retry_reason,
            )
            structured = self._request_and_parse(retry_prompt, raw_article, plan)

        return GeneratedArticlePayload(
            title=structured["title"],
            summary=structured.get("summary"),
            body=structured["body"],
            category=structured.get("category") or "geral",
            tags=structured.get("tags") or [],
            prompt_version=plan.prompt_version,
        )

    def _build_generation_plan(self, raw_article: RawArticle) -> GenerationPlan:
        source_text = remove_structured_noise(raw_article.original_content) or remove_structured_noise(
            raw_article.original_description
        )
        source_length = len(source_text)

        if source_length >= 2600:
            return GenerationPlan(
                source_summary_limit=700,
                source_body_limit=5200,
                fallback_body_limit=3200,
                target_body_min=2200,
                target_body_max=4200,
                paragraph_range="5 a 7",
            )

        if source_length >= 1400:
            return GenerationPlan(
                source_summary_limit=600,
                source_body_limit=4200,
                fallback_body_limit=2600,
                target_body_min=1600,
                target_body_max=3200,
                paragraph_range="4 a 6",
            )

        if source_length >= 700:
            return GenerationPlan(
                source_summary_limit=520,
                source_body_limit=3200,
                fallback_body_limit=2200,
                target_body_min=1100,
                target_body_max=2400,
                paragraph_range="3 a 5",
            )

        return GenerationPlan(
            source_summary_limit=420,
            source_body_limit=2400,
            fallback_body_limit=1700,
            target_body_min=800,
            target_body_max=1800,
            paragraph_range="3 a 4",
        )

    def _request_and_parse(self, prompt: str, raw_article: RawArticle, plan: GenerationPlan) -> dict[str, Any]:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        raw_text = getattr(response, "text", "") or ""
        return self._parse_model_response(raw_text, raw_article, plan)

    def _build_prompt(self, raw_article: RawArticle, prompt_template: str, plan: GenerationPlan) -> str:
        source_description = build_source_summary(
            raw_article.original_description,
            raw_article.original_content,
            limit=plan.source_summary_limit,
        )
        source_content = build_source_body(
            raw_article.original_content,
            raw_article.original_description,
            limit=plan.source_body_limit,
        )

        return (
            f"{prompt_template}\n\n"
            "Responda somente com JSON valido no formato:\n"
            '{"title":"", "summary":"", "body":"", "category":"", "tags":[""]}\n\n'
            "TAMANHO DESEJADO:\n"
            "- summary: 320 a 600 caracteres, direto e informativo\n"
            f"- body: aproximadamente {plan.target_body_min} a {plan.target_body_max} caracteres\n"
            f"- body com {plan.paragraph_range} paragrafos curtos ou medios\n"
            "- se a fonte for curta, aproveite ao maximo as informacoes disponiveis sem inventar fatos\n"
            "- nao repita a mesma ideia em varias frases so para aumentar tamanho\n\n"
            f"TITULO ORIGINAL: {raw_article.original_title}\n"
            f"DESCRICAO ORIGINAL: {source_description}\n"
            f"AUTOR ORIGINAL: {raw_article.original_author or ''}\n"
            f"URL ORIGINAL: {raw_article.original_url}\n"
            f"CONTEUDO ORIGINAL:\n{source_content}\n"
        )

    def _build_retry_prompt(
        self,
        raw_article: RawArticle,
        prompt_template: str,
        previous_payload: dict[str, Any],
        plan: GenerationPlan,
        retry_reason: str,
    ) -> str:
        draft_json = json.dumps(previous_payload, ensure_ascii=False)
        return (
            f"{self._build_prompt(raw_article, prompt_template, plan)}\n"
            "ATENCAO EXTRA:\n"
            f"- a resposta anterior teve este problema principal: {retry_reason}\n"
            "- reescreva TODOS os campos em portugues do Brasil natural\n"
            "- use acentuacao UTF-8 correta\n"
            "- nunca devolva palavras quebradas como lanÃ§amento, ambiÃ§Ã£o ou informaÃ§Ã£o\n"
            "- se a fonte original estiver em ingles, traduza o sentido para portugues do Brasil\n"
            "- entregue um body jornalistico mais desenvolvido, sem inflar artificialmente o texto\n"
            "- responda somente com JSON valido\n\n"
            f"RASCUNHO ANTERIOR:\n{draft_json}\n"
        )

    def _parse_model_response(self, raw_response: str, raw_article: RawArticle, plan: GenerationPlan) -> dict[str, Any]:
        raw_response = self._extract_json_object(raw_response)

        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError:
            payload = {}

        fallback_summary = build_source_summary(
            raw_article.original_description,
            raw_article.original_content,
            limit=plan.source_summary_limit,
        )
        fallback_body = build_source_body(
            raw_article.original_content,
            raw_article.original_description,
            limit=plan.fallback_body_limit,
        )

        title = self._as_text(payload.get("title")) or raw_article.original_title
        summary = self._as_optional_text(payload.get("summary")) or fallback_summary
        body = self._as_text(payload.get("body")) or fallback_body
        category = self._as_text(payload.get("category")) or "geral"
        tags = self._normalize_tags(payload.get("tags"))

        cleaned_title = normalize_generated_title(title, raw_article.original_title)
        cleaned_summary = self._sanitize_optional_text(summary)
        cleaned_body = sanitize_article_text(body)

        if is_suspicious_generated_text(cleaned_summary, min_length=60):
            cleaned_summary = fallback_summary or None

        if is_suspicious_generated_text(cleaned_body, min_length=120):
            cleaned_body = fallback_body

        cleaned_summary = truncate_text(cleaned_summary, 420) if cleaned_summary else None
        cleaned_body = truncate_text(cleaned_body, plan.target_body_max)

        return {
            "title": cleaned_title,
            "summary": cleaned_summary,
            "body": cleaned_body,
            "category": sanitize_article_text(category),
            "tags": tags,
        }

    def _extract_json_object(self, text: str) -> str:
        text = (text or "").strip()

        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]

        return text

    def _get_retry_reason(
        self,
        structured: dict[str, Any],
        raw_article: RawArticle,
        plan: GenerationPlan,
    ) -> Optional[str]:
        fields_to_check = [
            structured.get("title"),
            structured.get("summary"),
            structured.get("body"),
        ]

        if any("Ã" in (field or "") or "�" in (field or "") for field in fields_to_check):
            return "encoding quebrado"

        english_fields = sum(1 for field in fields_to_check if is_probably_english_text(field))
        if english_fields >= 2:
            return "texto ainda em ingles"

        generated_title = sanitize_article_text(structured.get("title"))
        source_title = sanitize_article_text(raw_article.original_title)
        if (
            generated_title
            and source_title
            and generated_title.casefold() == source_title.casefold()
            and is_probably_english_text(generated_title, min_tokens=4)
        ):
            return "titulo permaneceu em ingles"

        body = sanitize_article_text(structured.get("body"))
        source_body = remove_structured_noise(raw_article.original_content) or remove_structured_noise(
            raw_article.original_description
        )
        minimum_expected = max(700, int(plan.target_body_min * 0.55))
        if len(source_body) >= 1200 and len(body) < minimum_expected:
            return "corpo curto demais para a riqueza da fonte"

        return None

    def _normalize_tags(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [self._as_text(item) for item in value if self._as_text(item)]
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in value.split(",") if part.strip()]
        return []

    def _as_text(self, value: Any) -> str:
        if isinstance(value, str):
            return repair_text_encoding(value).strip()
        return ""

    def _as_optional_text(self, value: Any) -> Optional[str]:
        text = self._as_text(value)
        return text or None

    def _sanitize_optional_text(self, value: Optional[str]) -> Optional[str]:
        text = sanitize_article_text(value)
        return text or None