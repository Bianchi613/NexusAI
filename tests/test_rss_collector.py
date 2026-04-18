import xml.etree.ElementTree as ET

from app.collectors.rss import RSSCollector


def test_rss_normalize_item_separates_images_and_videos() -> None:
    collector = RSSCollector()
    xml = """
    <item xmlns:media="http://search.yahoo.com/mrss/">
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
