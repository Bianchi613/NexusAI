import hashlib
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


def is_article_candidate(
    title: Optional[str],
    description: Optional[str],
    content: Optional[str],
    url: Optional[str],
    *,
    blocked_terms: list[str],
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
