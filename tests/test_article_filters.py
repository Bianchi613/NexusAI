"""Testes focados nas funcoes utilitarias de limpeza e extracao de midia."""

from app.core.article_filters import (
    collect_image_urls,
    collect_video_urls,
    extract_video_urls_from_html,
    is_probable_image_url,
    is_probable_video_url,
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
