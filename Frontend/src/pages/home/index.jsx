import { useEffect, useState } from 'react'
import './home.css'
import mark from '../../../logos/Icon_Nexus_1.png'
import WatchStrip from '../../components/watch-strip/index.jsx'
import { mostRead, sectionSummaries } from '../../data/portalData'
import { ApiError, fetchHomeData } from '../../services/portal-api'

function getCarouselSlice(items, start, count) {
  if (items.length === 0) {
    return []
  }

  return Array.from({ length: count }, (_, index) => items[(start + index) % items.length])
}

function HomePage({ activeSection, onChangePage, onOpenArticle }) {
  const [homeData, setHomeData] = useState(null)
  const [status, setStatus] = useState('loading')
  const [errorMessage, setErrorMessage] = useState('')
  const [carouselStart, setCarouselStart] = useState(0)

  useEffect(() => {
    let isActive = true

    const loadHome = async () => {
      setStatus('loading')
      setErrorMessage('')

      try {
        const data = await fetchHomeData()
        if (!isActive) {
          return
        }
        setHomeData(data)
        setStatus('success')
      } catch (error) {
        if (!isActive) {
          return
        }
        setStatus('error')
        setErrorMessage(
          error instanceof ApiError
            ? error.message
            : 'Nao foi possivel carregar a home do portal.',
        )
      }
    }

    loadHome()

    return () => {
      isActive = false
    }
  }, [])

  const sectionSummary = sectionSummaries[activeSection] ?? sectionSummaries.Home
  const summary = sectionSummary ?? sectionSummaries.Inicio
  const heroArticle = homeData?.heroArticle
  const latestArticles = homeData?.latestArticles ?? []
  const watchArticles = homeData?.watchArticles ?? []
  const featuredCategories = homeData?.featuredCategories ?? []
  const visibleWatchStories = getCarouselSlice(watchArticles, carouselStart, Math.min(4, watchArticles.length))

  if (status === 'loading') {
    return (
      <section className="editorial-placeholder">
        <p className="story-kicker">Carregando home</p>
        <h1>Buscando os destaques publicados do portal.</h1>
        <p>Assim que a API responder, a capa sera montada com os blocos reais vindos do backend.</p>
      </section>
    )
  }

  if (status === 'error' || !heroArticle) {
    return (
      <section className="editorial-placeholder">
        <p className="story-kicker">Home indisponivel</p>
        <h1>Nao foi possivel carregar a capa do portal.</h1>
        <p>{errorMessage || 'Tente novamente quando o backend estiver disponivel.'}</p>
      </section>
    )
  }

  return (
    <section className="home-page">
      <div className="hero-grid">
        <article className="hero-main">
          {heroArticle.imageUrl ? (
            <div className="hero-main__media">
              <img src={heroArticle.imageUrl} alt={heroArticle.title} />
            </div>
          ) : null}

          <div className="hero-label-row">
            <p className="story-kicker">{activeSection}</p>
            <span className="hero-live-pill">Edicao ao vivo</span>
          </div>

          <h1>{heroArticle.title}</h1>
          <p className="hero-summary">{heroArticle.summary || summary}</p>

          <div className="hero-actions">
            <button className="primary-link" type="button" onClick={() => onOpenArticle(heroArticle.slug)}>
              Ler materia
            </button>
            <button
              className="text-link"
              type="button"
              onClick={() => onChangePage(heroArticle.page)}
            >
              Ir para {heroArticle.category}
            </button>
          </div>

          <div className="hero-meta">
            <span>{heroArticle.publishedAt}</span>
            <span>{heroArticle.author}</span>
            <span>{heroArticle.readTime}</span>
            <span>{heroArticle.location}</span>
          </div>

          <div className="hero-metrics">
            <div>
              <strong>{latestArticles.length}</strong>
              <span>Materias no bloco principal</span>
            </div>
            <div>
              <strong>{featuredCategories.length}</strong>
              <span>Editorias destacadas</span>
            </div>
            <div>
              <strong>{watchArticles.length}</strong>
              <span>Materias extras na faixa inferior</span>
            </div>
          </div>
        </article>

        <aside className="hero-rail">
          <div className="hero-visual">
            <div className="hero-visual-mark">
              <img src={mark} alt="" />
            </div>
            <div className="hero-visual-copy">
              <p className="story-kicker">Visao da plataforma</p>
              <h2>Mais proximo de uma capa de jornal digital do que de uma landing generica.</h2>
              <p>
                A primeira dobra organiza hierarquia, ritmo e contraste para que as noticias
                ocupem o centro da experiencia.
              </p>
            </div>
          </div>

          <div className="rail-panel">
            <div className="rail-panel-head">
              <h3>Mais lidas</h3>
              <p>Leitura recorrente com mais peso editorial.</p>
            </div>
            <ol className="most-read-list">
              {(latestArticles.length > 0 ? latestArticles : mostRead).slice(0, 5).map((story) => (
                <li key={story.title ?? story}>{story.title ?? story}</li>
              ))}
            </ol>
          </div>
        </aside>
      </div>

      <section className="news-grid-section">
        <div className="section-bar">
          <div>
            <p className="story-kicker">Pulso do portal</p>
            <h2>Ultimas do Nexus IA</h2>
          </div>
          <p>Materias publicadas pelo backend e prontas para leitura no frontend.</p>
        </div>

        <div className="news-grid">
          {latestArticles.slice(1).map((story) => (
            <button
              className="news-card"
              key={story.slug}
              type="button"
              onClick={() => onOpenArticle(story.slug)}
            >
              {story.imageUrl ? (
                <div className="news-card__media">
                  <img src={story.imageUrl} alt={story.title} />
                </div>
              ) : null}
              <p className="story-kicker">{story.category}</p>
              <h3>{story.title}</h3>
              <p>{story.excerpt || story.summary}</p>
            </button>
          ))}
        </div>
      </section>

      {watchArticles.length > 0 ? (
        <WatchStrip
          stories={visibleWatchStories}
          onNext={() => {
            setCarouselStart((current) => (current + 1) % watchArticles.length)
          }}
          onPrevious={() => {
            setCarouselStart((current) => (current - 1 + watchArticles.length) % watchArticles.length)
          }}
          onOpenArticle={onOpenArticle}
        />
      ) : null}

      <div className="secondary-grid">
        {featuredCategories.map((category) => (
          <button
            className="secondary-story"
            key={category.page}
            type="button"
            onClick={() => onChangePage(category.page)}
          >
            {category.featuredArticle?.imageUrl ? (
              <div className="secondary-story__media">
                <img
                  src={category.featuredArticle.imageUrl}
                  alt={category.featuredArticle.title}
                />
              </div>
            ) : null}
            <p className="story-kicker">{category.eyebrow}</p>
            <h2>{category.title}</h2>
            <p>{category.description}</p>
            <span className="secondary-story__link">
              {category.featuredArticle ? category.featuredArticle.title : 'Abrir editoria'}
            </span>
          </button>
        ))}
      </div>
    </section>
  )
}

export default HomePage
