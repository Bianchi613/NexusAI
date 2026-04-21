import { useState } from 'react'
import { getArticlesByPage, getCategoryContent } from '../../data/contentData'
import './editorial-page.css'

function getCarouselSlice(items, start, count) {
  if (items.length === 0) {
    return []
  }

  return Array.from({ length: count }, (_, index) => {
    return items[(start + index) % items.length]
  })
}

function EditorialPage({ page, onOpenArticle }) {
  const content = getCategoryContent(page)
  const articles = getArticlesByPage(page)
  const featuredArticle = articles[0]
  const carouselPool = articles.slice(1)
  const [carouselStart, setCarouselStart] = useState(0)
  const visibleArticles = getCarouselSlice(
    carouselPool,
    carouselStart,
    Math.min(3, carouselPool.length),
  )

  if (!content || !featuredArticle) {
    return null
  }

  return (
    <section className="editorial-page">
      <div className="editorial-page__lead">
        <div className="editorial-page__meta">
          <p className="story-kicker">{content.eyebrow}</p>
          <span className="editorial-page__pill">{articles.length} materias na faixa</span>
        </div>

        <h1>{content.title}</h1>
        <p className="editorial-page__description">{content.description}</p>
      </div>

      <div className="editorial-page__grid">
        <article className="editorial-page__feature">
          <div className="editorial-page__feature-copy">
            <p className="story-kicker">{featuredArticle.label}</p>
            <h2>{featuredArticle.title}</h2>
            <p>{featuredArticle.summary}</p>
          </div>

          <div className="editorial-page__feature-meta">
            <span>{featuredArticle.author}</span>
            <span>{featuredArticle.publishedAt}</span>
            <span>{featuredArticle.readTime}</span>
          </div>

          <div className="editorial-page__feature-actions">
            <button
              className="primary-link"
              type="button"
              onClick={() => onOpenArticle(featuredArticle.slug)}
            >
              Ler materia
            </button>
            <span className="editorial-page__location">{featuredArticle.location}</span>
          </div>
        </article>

        <aside className="editorial-page__rail">
          <p className="editorial-page__label">{content.railTitle}</p>
          <ul>
            {content.railItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </aside>
      </div>

      <section className="editorial-page__carousel">
        <div className="section-bar">
          <div>
            <p className="story-kicker">Carrossel da editoria</p>
            <h2>Materias em destaque</h2>
          </div>

          {carouselPool.length > 1 ? (
            <div className="editorial-page__controls">
              <button
                type="button"
                aria-label="Materias anteriores"
                onClick={() => {
                  setCarouselStart((current) => {
                    return (current - 1 + carouselPool.length) % carouselPool.length
                  })
                }}
              >
                &lt;
              </button>
              <button
                type="button"
                aria-label="Proximas materias"
                onClick={() => {
                  setCarouselStart((current) => {
                    return (current + 1) % carouselPool.length
                  })
                }}
              >
                &gt;
              </button>
            </div>
          ) : null}
        </div>

        <div className="editorial-page__track">
          {visibleArticles.map((article) => (
            <button
              className="editorial-page__story-card"
              key={article.slug}
              type="button"
              onClick={() => onOpenArticle(article.slug)}
            >
              <span className="story-kicker">{article.label}</span>
              <h3>{article.title}</h3>
              <p>{article.excerpt}</p>
              <span className="editorial-page__story-link">Abrir materia</span>
            </button>
          ))}
        </div>
      </section>
    </section>
  )
}

export default EditorialPage
