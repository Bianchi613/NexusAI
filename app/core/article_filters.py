"""Funcoes utilitarias de limpeza, normalizacao e filtros do pipeline.

Este modulo e o "kit de higiene" do projeto. Ele concentra:
- normalizacao de texto e URL
- limpeza de HTML e ruido estrutural
- extracao e deduplicacao de imagens e videos
- regras de qualidade minima
- heuristicas simples de similaridade e categoria
"""

import hashlib
import html
import re
import unicodedata
from typing import Any, Optional
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

# Stopwords usadas apenas na heuristica simples de similaridade entre titulos.
TITLE_SIMILARITY_STOPWORDS = {
    "a",
    "o",
    "os",
    "as",
    "um",
    "uma",
    "uns",
    "umas",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "e",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "para",
    "por",
    "com",
    "sem",
    "sobre",
    "apos",
    "apos",
    "the",
    "and",
    "for",
    "with",
    "from",
    "after",
    "into",
    "its",
}


def normalize_text(value: Optional[str]) -> str:
    """Remove excesso de espacos e normaliza acentos para comparacoes."""
    if not value:
        return ""

    collapsed = re.sub(r"\s+", " ", value).strip()
    normalized = unicodedata.normalize("NFKD", collapsed).encode("ascii", "ignore").decode("ascii")
    return normalized


def strip_html(value: Optional[str]) -> str:
    """Remove tags HTML e preserva quebras de bloco relevantes."""
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
    """Aplica limpeza de HTML e remove ruido editorial comum nas fontes."""
    text = strip_html(value)
    text = re.sub(r"(?i)\bveja os v[ií]deos que est[aã]o em alta no g1\b", " ", text)
    text = re.sub(r"(?i)\breprodu[cç][aã]o\s*/?\s*[a-z0-9._-]+\b", " ", text)
    text = re.sub(r"(?i)\bsaiba mais sobre .*?$", " ", text)
    text = re.sub(r"\.\.\.+", ". ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_structured_noise(value: Optional[str]) -> str:
    """Corta blocos estruturados ou institucionais no final do texto."""
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
    """Encurta texto preservando corte mais natural quando possivel."""
    text = remove_structured_noise(value)
    if len(text) <= limit:
        return text

    shortened = text[:limit].rsplit(" ", 1)[0].strip()
    return (shortened or text[:limit]).strip() + "..."


def first_sentences(value: Optional[str], *, max_sentences: int, max_chars: int) -> str:
    """Seleciona apenas as primeiras sentencas uteis de um texto longo."""
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
    """Monta um resumo curto da materia de origem."""
    base = description or content
    return first_sentences(base, max_sentences=2, max_chars=limit)


def build_source_body(content: Optional[str], description: Optional[str], limit: int = 1400) -> str:
    """Monta um corpo-base curto e limpo para o prompt da IA."""
    base = content or description
    return first_sentences(base, max_sentences=6, max_chars=limit)


def is_suspicious_generated_text(value: Optional[str], *, min_length: int = 30) -> bool:
    """Detecta saidas do modelo com cara de lixo, truncamento ou HTML cru."""
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
    """Normaliza titulo para comparacao exata aproximada."""
    normalized = normalize_text(value).lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalize_url(value: Optional[str]) -> str:
    """Padroniza URL e remove parametros de rastreamento."""
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
    """Gera hash estavel para apoiar deduplicacao de bruto."""
    base = f"{normalize_url(url)}|{normalize_title(title)}|{normalize_text(content).lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def extract_image_urls_from_html(value: Optional[str]) -> list[str]:
    """Extrai imagens de HTML simples usando regex defensiva."""
    if not value:
        return []

    urls = re.findall(r"""<img[^>]+src=["']([^"']+)["']""", value, flags=re.IGNORECASE)
    return deduplicate_urls(urls)


def extract_video_urls_from_html(value: Optional[str]) -> list[str]:
    """Extrai videos e embeds de HTML simples."""
    if not value:
        return []

    urls: list[str] = []
    urls.extend(re.findall(r"""<(?:iframe|video|source)[^>]+src=["']([^"']+)["']""", value, flags=re.IGNORECASE))
    return deduplicate_urls(urls)


def deduplicate_urls(values: list[str]) -> list[str]:
    """Normaliza e remove URLs repetidas preservando ordem."""
    unique_urls: list[str] = []
    seen: set[str] = set()

    for value in values:
        normalized = normalize_url(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_urls.append(normalized)

    return unique_urls


def collect_image_urls(*values: Any) -> list[str]:
    """Percorre estruturas heterogeneas e coleta apenas imagens."""
    collected: list[str] = []

    for value in values:
        if not value:
            continue

        if isinstance(value, str):
            normalized = normalize_url(value)
            if normalized:
                collected.append(normalized)
            continue

        if isinstance(value, list):
            collected.extend(collect_image_urls(*value))
            continue

        if isinstance(value, dict):
            candidate_keys = (
                "url",
                "src",
                "image",
                "image_url",
                "imageUrl",
                "thumbnail",
                "thumbnail_url",
                "thumbnailUrl",
            )
            for key in candidate_keys:
                if key in value:
                    collected.extend(collect_image_urls(value.get(key)))

    return deduplicate_urls(collected)


def collect_video_urls(*values: Any) -> list[str]:
    """Percorre estruturas heterogeneas e coleta apenas videos."""
    collected: list[str] = []

    for value in values:
        if not value:
            continue

        if isinstance(value, str):
            normalized = normalize_url(value)
            if normalized:
                collected.append(normalized)
            continue

        if isinstance(value, list):
            collected.extend(collect_video_urls(*value))
            continue

        if isinstance(value, dict):
            candidate_keys = (
                "url",
                "src",
                "video",
                "video_url",
                "videoUrl",
                "embed",
                "embed_url",
                "embedUrl",
            )
            for key in candidate_keys:
                if key in value:
                    collected.extend(collect_video_urls(value.get(key)))

    return deduplicate_urls(collected)


def is_probable_image_url(value: Optional[str]) -> bool:
    """Heuristica simples para separar imagem de video/embed."""
    normalized = normalize_url(value)
    if not normalized:
        return False

    lowered = normalized.lower()
    blocked_fragments = (
        "youtube.com/embed/",
        "youtube.com/watch",
        "youtu.be/",
        ".mp4",
        ".webm",
        ".m3u8",
    )
    if any(fragment in lowered for fragment in blocked_fragments):
        return False

    image_markers = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
        ".svg",
        ".avif",
        "/image/",
        "/images/",
        "/photo/",
        "/photos/",
    )
    return any(marker in lowered for marker in image_markers)


def is_probable_video_url(value: Optional[str]) -> bool:
    """Heuristica simples para identificar URL com cara de video."""
    normalized = normalize_url(value)
    if not normalized:
        return False

    lowered = normalized.lower()
    video_markers = (
        "youtube.com/embed/",
        "youtube.com/watch",
        "youtu.be/",
        "vimeo.com/",
        ".mp4",
        ".webm",
        ".m3u8",
        "/video/",
        "/videos/",
    )
    return any(marker in lowered for marker in video_markers)


def score_article_quality(title: Optional[str], description: Optional[str], content: Optional[str]) -> int:
    """Atribui um score minimo com base em completude do item bruto."""
    score = 0

    if len((title or "").strip()) >= 20:
        score += 1
    if len((description or "").strip()) >= 40:
        score += 1
    if len((content or "").strip()) >= 80:
        score += 1

    return score


def contains_blocked_term(title: Optional[str], blocked_terms: list[str]) -> bool:
    """Verifica termos que sugerem publicidade ou baixo valor editorial."""
    normalized_title = normalize_title(title)
    if not normalized_title:
        return False

    for term in blocked_terms:
        normalized_term = normalize_title(term)
        if normalized_term and normalized_term in normalized_title:
            return True

    return False


def starts_with_blocked_prefix(title: Optional[str], blocked_prefixes: list[str]) -> bool:
    """Bloqueia prefixos com cara de clickbait ou texto promocional."""
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
    """Decide se um item bruto merece seguir no pipeline."""
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
    """Converte labels em slug simples e estavel."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "geral"


def normalize_label(value: str) -> str:
    """Padroniza labels para categoria e tag mantendo siglas curtas."""
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
    """Limpa e adapta titulos gerados para um tom mais editorial."""
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


def title_similarity_tokens(value: Optional[str]) -> set[str]:
    """Quebra titulo em tokens relevantes para comparar sem stopwords."""
    normalized = normalize_title(value)
    tokens = {
        token
        for token in normalized.split()
        if len(token) >= 3 and token not in TITLE_SIMILARITY_STOPWORDS and not token.isdigit()
    }
    return tokens


def are_titles_similar(left: Optional[str], right: Optional[str]) -> bool:
    """Heuristica simples de similaridade para evitar quase-duplicatas."""
    normalized_left = normalize_title(left)
    normalized_right = normalize_title(right)
    if not normalized_left or not normalized_right:
        return False
    if normalized_left == normalized_right:
        return True

    left_tokens = title_similarity_tokens(left)
    right_tokens = title_similarity_tokens(right)
    if not left_tokens or not right_tokens:
        return False

    common_tokens = left_tokens & right_tokens
    if len(common_tokens) < 3:
        return False

    smaller_size = min(len(left_tokens), len(right_tokens))
    if smaller_size == 0:
        return False

    overlap_ratio = len(common_tokens) / smaller_size
    union_size = len(left_tokens | right_tokens)
    jaccard_ratio = len(common_tokens) / union_size if union_size else 0.0

    return overlap_ratio >= 0.75 or jaccard_ratio >= 0.6


def guess_category_from_article(
    title: Optional[str],
    description: Optional[str] = None,
    *,
    source_name: Optional[str] = None,
) -> str:
    """Tenta inferir categoria com base em fonte, titulo e descricao."""
    text = normalize_title(" ".join(part for part in [source_name or "", title or "", description or ""] if part))

    keyword_groups = [
        (
            "Esportes",
            {"futebol", "basquete", "tenis", "esporte", "jogador", "partida", "campeonato", "gol", "nba", "nfl"},
        ),
        (
            "Politica",
            {
                "camara",
                "senado",
                "congresso",
                "governo",
                "presidente",
                "deputado",
                "senador",
                "politica",
                "ministerio",
                "eleicao",
                "plenario",
                "comissao",
            },
        ),
        (
            "Saude",
            {"saude", "hospital", "medico", "vacina", "doenca", "virus", "tratamento", "medicina"},
        ),
        (
            "Negocios",
            {
                "mercado",
                "economia",
                "bolsa",
                "varejo",
                "investimento",
                "receita",
                "lucro",
                "empresa",
                "banco",
                "inflacao",
                "credito",
                "negocio",
            },
        ),
        (
            "Espaco",
            {"nasa", "artemis", "espaco", "orbita", "satelite", "astronauta", "foguete", "lua", "marte"},
        ),
        (
            "Ciencia",
            {"ciencia", "cientista", "estudo", "pesquisa", "laboratorio", "nature", "sciencedaily", "descoberta"},
        ),
        (
            "Tecnologia",
            {
                "tecnologia",
                "tecnoblog",
                "canaltech",
                "olhar digital",
                "techcrunch",
                "wired",
                "ars technica",
                "software",
                "app",
                "aplicativo",
                "apple",
                "google",
                "microsoft",
                "chip",
                "ia",
                "ai",
                "iphone",
                "android",
                "pc",
                "smartphone",
                "app store",
            },
        ),
    ]

    for category, keywords in keyword_groups:
        if any(keyword in text for keyword in keywords):
            return category

    return "Geral"
