"""Testes do coletor JSON Feed com foco em midias e normalizacao."""

from app.collectors.json_feed import JSONFeedCollector


def test_json_feed_normalize_item_collects_media_without_external_url_as_video() -> None:
    """Valida a separacao correta entre imagens, videos e links externos."""
    collector = JSONFeedCollector()
    item = {
        "id": "json-feed-1",
        "url": "https://example.com/news/json-feed-story",
        "external_url": "https://external.example.com/reference-story",
        "title": "JSON Feed de teste gera noticia com imagens e videos",
        "summary": "Resumo suficiente para o item passar pelo filtro do pipeline sem problemas.",
        "content_html": (
            "<p>Conteudo extenso o bastante para passar pelo filtro atual do sistema.</p>"
            '<img src="https://cdn.example.com/inline-image.jpg">'
            '<iframe src="https://www.youtube.com/embed/jsonfeed123"></iframe>'
        ),
        "image": "https://cdn.example.com/cover.jpg",
        "attachments": [
            {"url": "https://cdn.example.com/gallery-1.png", "mime_type": "image/png"},
            {"url": "https://cdn.example.com/video.mp4", "mime_type": "video/mp4"},
        ],
        "authors": [{"name": "Equipe Nexus"}],
        "date_published": "2026-04-18T12:00:00Z",
    }

    raw_article = collector._normalize_item(7, item)

    assert raw_article is not None
    assert raw_article.original_image_urls == [
        "https://cdn.example.com/cover.jpg",
        "https://cdn.example.com/gallery-1.png",
        "https://cdn.example.com/inline-image.jpg",
    ]
    assert raw_article.original_video_urls == [
        "https://cdn.example.com/video.mp4",
        "https://www.youtube.com/embed/jsonfeed123",
    ]
    assert "https://external.example.com/reference-story" not in raw_article.original_video_urls
