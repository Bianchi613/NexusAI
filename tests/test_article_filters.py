"""Testes focados nas funcoes utilitarias de limpeza e extracao de midia."""

from Engine.app.core.article_filters import (
    build_fallback_tags,
    collect_image_urls,
    collect_video_urls,
    extract_video_urls_from_html,
    is_probably_english_text,
    is_probable_image_url,
    is_probable_video_url,
    repair_text_encoding,
)


def test_collect_image_urls_deduplicates_and_normalizes() -> None:
    """Garante que imagens repetidas sejam normalizadas e deduplicadas."""
    urls = collect_image_urls(
        "https://example.com/image.jpg?utm_source=test",
        "https://example.com/image.jpg",
        {"image": "https://example.com/gallery/photo.png"},
    )

    assert urls == [
        "https://example.com/image.jpg",
        "https://example.com/gallery/photo.png",
    ]


def test_video_helpers_keep_video_separate_from_images() -> None:
    """Confirma que embeds e videos nao vazam para a lista de imagens."""
    html = """
    <div>
      <iframe src="https://www.youtube.com/embed/abc123"></iframe>
      <video src="https://cdn.example.com/video.mp4"></video>
    </div>
    """

    assert is_probable_image_url("https://www.youtube.com/embed/abc123") is False
    assert is_probable_video_url("https://www.youtube.com/embed/abc123") is True
    assert extract_video_urls_from_html(html) == [
        "https://www.youtube.com/embed/abc123",
        "https://cdn.example.com/video.mp4",
    ]

    assert collect_video_urls(
        "https://www.youtube.com/embed/abc123",
        {"video_url": "https://cdn.example.com/video.mp4"},
    ) == [
        "https://www.youtube.com/embed/abc123",
        "https://cdn.example.com/video.mp4",
    ]


def test_repair_text_encoding_fixes_common_mojibake() -> None:
    """Corrige textos UTF-8 quebrados por leitura errada."""
    assert repair_text_encoding("lanÃ§amento") == "lançamento"
    assert repair_text_encoding("ambiÃ§Ã£o") == "ambição"


def test_is_probably_english_text_detects_english_sentence() -> None:
    """Distingue saida longa em ingles de texto em portugues."""
    assert (
        is_probably_english_text(
            "Leader of leftwing Economic Freedom Fighters was convicted last year for firing rifle in the air."
    )
        is True
    )
    assert is_probably_english_text("O governo anunciou novas medidas para o setor de tecnologia no Brasil.") is False


def test_build_fallback_tags_generates_useful_tags_from_title_and_source() -> None:
    """Gera tags locais quando a IA nao devolve nada."""
    tags = build_fallback_tags(
        title="Vídeo: Davi Alcolumbre manifesta pesar pela morte de Oscar Schmidt",
        summary=(
            'Nesta sexta-feira, o presidente do Senado lamentou o falecimento '
            'de Oscar Schmidt, ex-jogador de basquete.'
        ),
        category="Geral",
        source_name="Senado Noticias",
        max_tags=5,
    )

    assert "Senado" in tags
    assert "Davi Alcolumbre" in tags
    assert "Oscar Schmidt" in tags
