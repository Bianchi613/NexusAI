"""Testes do coletor RSS com foco na separacao de midias."""

import xml.etree.ElementTree as ET
from types import SimpleNamespace

from app.collectors.rss import RSSCollector


def test_rss_normalize_item_separates_images_and_videos() -> None:
    """Confirma que o RSS separa corretamente imagens e videos embutidos."""
    collector = RSSCollector()
    xml = """
    <item xmlns:media="urn:media-rss">
      <title>RSS de teste separa imagem e video corretamente no pipeline</title>
      <link>https://example.com/rss/test-story</link>
      <guid>rss-test-1</guid>
      <description>
        <![CDATA[
          <p>Descricao suficientemente longa para passar pelo filtro do projeto.</p>
          <img src="https://cdn.example.com/description-image.jpg" />
          <iframe src="https://www.youtube.com/embed/rssvideo123"></iframe>
        ]]>
      </description>
      <pubDate>Sat, 18 Apr 2026 12:00:00 GMT</pubDate>
      <enclosure url="https://cdn.example.com/trailer.mp4" type="video/mp4" />
      <enclosure url="https://cdn.example.com/card.jpg" type="image/jpeg" />
      <media:thumbnail url="https://cdn.example.com/thumb.png" />
    </item>
    """
    item = ET.fromstring(xml)

    raw_article = collector._normalize_item(11, item)

    assert raw_article is not None
    assert raw_article.original_image_urls == [
        "https://cdn.example.com/card.jpg",
        "https://cdn.example.com/thumb.png",
        "https://cdn.example.com/description-image.jpg",
    ]
    assert raw_article.original_video_urls == [
        "https://cdn.example.com/trailer.mp4",
        "https://www.youtube.com/embed/rssvideo123",
    ]


def test_rss_normalize_item_enriches_media_from_original_page(monkeypatch) -> None:
    """Completa imagem e video quando o feed nao traz midia suficiente."""
    collector = RSSCollector()
    xml = """
    <item>
      <title>Materia sem midia no feed mas com midia na pagina original</title>
      <link>https://example.com/noticia/teste</link>
      <guid>rss-test-2</guid>
      <description>
        <![CDATA[
          <p>Descricao suficientemente longa para passar pelo filtro do projeto.</p>
        ]]>
      </description>
      <pubDate>Sat, 18 Apr 2026 12:00:00 GMT</pubDate>
    </item>
    """
    item = ET.fromstring(xml)

    page_html = """
    <html>
      <head>
        <meta property="og:image" content="https://cdn.example.com/cover.jpg" />
        <meta property="og:video" content="https://www.youtube.com/embed/pagevideo123" />
      </head>
      <body></body>
    </html>
    """

    def fake_get(url, timeout, headers):
        return SimpleNamespace(
            status_code=200,
            text=page_html,
            encoding="utf-8",
            apparent_encoding="utf-8",
            raise_for_status=lambda: None,
        )

    monkeypatch.setattr("app.collectors.rss.requests.get", fake_get)

    raw_article = collector._normalize_item(22, item)

    assert raw_article is not None
    assert raw_article.original_image_urls == ["https://cdn.example.com/cover.jpg"]
    assert raw_article.original_video_urls == ["https://www.youtube.com/embed/pagevideo123"]
