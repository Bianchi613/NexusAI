import hashlib
import html
import re
import unicodedata
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
    "source",
}


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""

    collapsed = re.sub(r"\s+", " ", value).strip()
    normalized = unicodedata.normalize("NFKD", collapsed).encode("ascii", "ignore").decode("ascii")
    return normalized


def strip_html(value: Optional[str]) -> str:
    if not value:
        return ""

    text = html.unescape(value)
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?is)<table.*?>.*?</table>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n", text)
    text = re.sub(r"(?i)</div\s*>", "\n", text)
    text = re.sub(r"(?i)</li\s*>", "\n", text)
    text = re.sub(r"(?i)<li[^>]*>", "- ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def sanitize_article_text(value: Optional[str]) -> str:
    text = strip_html(value)
    text = re.sub(r"(?i)\bveja os v[ií]deos que est[aã]o em alta no g1\b", " ", text)
    text = re.sub(r"(?i)\breprodu[cç][aã]o\s*/?\s*[a-z0-9._-]+\b", " ", text)
    text = re.sub(r"(?i)\bsaiba mais sobre .*?$", " ", text)
    text = re.sub(r"\.\.\.+", ". ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_structured_noise(value: Optional[str]) -> str:
    text = sanitize_article_text(value)
    if not text:
        return ""

    cut_markers = [
        " Tabela ",
        " Período ",
        " Fonte :",
        " Fonte:",
        " Saiba mais ",
    ]

    for marker in cut_markers:
        index = text.find(marker)
        if index > 150:
            text = text[:index].strip()
            break

    text = re.sub(r"(?i)\.\s*(review do|leia mais|veja mais|saiba mais)\b.*$", ".", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate_text(value: Optional[str], limit: int) -> str:
    text = remove_structured_noise(value)
    if len(text) <= limit:
        return text

    shortened = text[:limit].rsplit(" ", 1)[0].strip()
    return (shortened or text[:limit]).strip() + "..."


def first_sentences(value: Optional[str], *, max_sentences: int, max_chars: int) -> str:
    text = remove_structured_noise(value)
    if not text:
        return ""

    parts = re.split(r"(?<=[.!?])\s+", text)
    selected: list[str] = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        selected.append(part)
        candidate = " ".join(selected)
        if len(selected) >= max_sentences or len(candidate) >= max_chars:
            return truncate_text(candidate, max_chars)

    return truncate_text(" ".join(selected), max_chars)


def build_source_summary(description: Optional[str], content: Optional[str], limit: int = 320) -> str:
    base = description or content
    return first_sentences(base, max_sentences=2, max_chars=limit)


def build_source_body(content: Optional[str], description: Optional[str], limit: int = 1400) -> str:
    base = content or description
    return first_sentences(base, max_sentences=6, max_chars=limit)


def is_suspicious_generated_text(value: Optional[str], *, min_length: int = 30) -> bool:
    text = sanitize_article_text(value)
    if not text:
        return True
    if len(text) < min_length:
        return True
    if "<" in text or ">" in text:
        return True
    if text.count("...") >= 2:
        return True
    return False


def normalize_title(value: Optional[str]) -> str:
    normalized = normalize_text(value).lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalize_url(value: Optional[str]) -> str:
    if not value:
        return ""

    parts = urlsplit(value.strip())
    filtered_query = [
        (key, item_value)
        for key, item_value in parse_qsl(parts.query, keep_blank_values=False)
        if not key.startswith("utm_") and key.lower() not in TRACKING_QUERY_KEYS
    ]
    path = parts.path.rstrip("/") or "/"

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            urlencode(filtered_query),
            "",
        )
    )


def build_content_hash(url: Optional[str], title: Optional[str], content: Optional[str]) -> str:
    base = f"{normalize_url(url)}|{normalize_title(title)}|{normalize_text(content).lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def score_article_quality(title: Optional[str], description: Optional[str], content: Optional[str]) -> int:
    score = 0

    if len((title or "").strip()) >= 20:
        score += 1
    if len((description or "").strip()) >= 40:
        score += 1
    if len((content or "").strip()) >= 80:
        score += 1

    return score


def contains_blocked_term(title: Optional[str], blocked_terms: list[str]) -> bool:
    normalized_title = normalize_title(title)
    if not normalized_title:
        return False

    for term in blocked_terms:
        normalized_term = normalize_title(term)
        if normalized_term and normalized_term in normalized_title:
            return True

    return False


def starts_with_blocked_prefix(title: Optional[str], blocked_prefixes: list[str]) -> bool:
    normalized_title = normalize_title(title)
    if not normalized_title:
        return False

    for prefix in blocked_prefixes:
        normalized_prefix = normalize_title(prefix)
        if normalized_prefix and normalized_title.startswith(normalized_prefix):
            return True

    return False


def is_article_candidate(
    title: Optional[str],
    description: Optional[str],
    content: Optional[str],
    url: Optional[str],
    *,
    blocked_terms: list[str],
    blocked_prefixes: list[str],
    min_title_length: int,
    min_content_length: int,
    min_quality_score: int,
) -> bool:
    if not title or not url:
        return False

    title = title.strip()
    description = (description or "").strip()
    content = (content or "").strip()

    if len(title) < min_title_length:
        return False
    if not description and not content:
        return False
    if len(content or description) < min_content_length:
        return False
    if contains_blocked_term(title, blocked_terms):
        return False
    if starts_with_blocked_prefix(title, blocked_prefixes):
        return False
    if score_article_quality(title, description, content) < min_quality_score:
        return False

    return True


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "geral"


def normalize_label(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    if not cleaned:
        return ""

    words = []
    for word in cleaned.split(" "):
        if word.isupper() and len(word) <= 5:
            words.append(word)
        else:
            words.append(word.capitalize())

    return " ".join(words)


def normalize_generated_title(title: Optional[str], source_title: Optional[str] = None) -> str:
    cleaned_title = sanitize_article_text(title)
    fallback_title = sanitize_article_text(source_title)

    title_for_rules = cleaned_title or fallback_title
    if not title_for_rules:
        return ""

    normalized = title_for_rules
    normalized = re.sub(r"(?i)^review do\s+", "Analise do ", normalized)
    normalized = re.sub(r"(?i)^review da\s+", "Analise da ", normalized)
    normalized = re.sub(r"(?i)^review de\s+", "Analise de ", normalized)
    normalized = re.sub(r"(?i)\breview\b", "Analise", normalized)
    normalized = re.sub(r"(?i)\bhands-on\b", "Primeiras impressoes", normalized)
    normalized = re.sub(r"(?i)\bpreview\b", "Previa", normalized)
    normalized = re.sub(r"(?i)\blive blog\b", "Cobertura ao vivo", normalized)

    english_markers = (" review", "hands-on", "preview", "live blog")
    if cleaned_title and any(marker in cleaned_title.lower() for marker in english_markers) and fallback_title:
        normalized = fallback_title

    normalized = re.sub(r"\s+", " ", normalized).strip(" -:")
    return normalized
