import { useEffect, useState } from 'react'
import './styles/app-shell.css'
import ArticlePage from './components/article-page/index.jsx'
import Footer from './components/footer/index.jsx'
import Header from './components/header/index.jsx'
import Sidebar from './components/sidebar/index.jsx'
import WatchStrip from './components/watch-strip/index.jsx'
import { getArticleBySlug, getRelatedArticles } from './data/contentData'
import { latestStories, watchStories } from './data/portalData'
import CienciaPage from './pages/ciencia/index.jsx'
import ClimaPage from './pages/clima/index.jsx'
import CulturaPage from './pages/cultura/index.jsx'
import HomePage from './pages/home/index.jsx'
import LoginPage from './pages/login/index.jsx'
import NegociosPage from './pages/negocios/index.jsx'
import NoticiasPage from './pages/noticias/index.jsx'
import NotFoundPage from './pages/not-found/index.jsx'
import PoliticaPage from './pages/politica/index.jsx'
import RegisterPage from './pages/register/index.jsx'
import SaudePage from './pages/saude/index.jsx'
import TecnologiaPage from './pages/tecnologia/index.jsx'
import VideosPage from './pages/videos/index.jsx'

const pageIds = new Set([
  'home',
  'register',
  'login',
  'not-found',
  'noticias',
  'negocios',
  'tecnologia',
  'saude',
  'clima',
  'cultura',
  'politica',
  'ciencia',
  'videos',
])

function getRouteFromHash() {
  if (typeof window === 'undefined') {
    return { page: 'home', activeNav: 'home', articleSlug: null }
  }

  const rawHash = window.location.hash.replace('#', '').trim()
  const normalizedHash = rawHash.toLowerCase()

  if (!normalizedHash) {
    return { page: 'home', activeNav: 'home', articleSlug: null }
  }

  if (normalizedHash === 'laboratorio-ia') {
    return { page: 'not-found', activeNav: '', articleSlug: null }
  }

  if (normalizedHash.startsWith('materia/')) {
    const articleSlug = normalizedHash.slice('materia/'.length)
    const article = getArticleBySlug(articleSlug)

    if (!article) {
      return { page: 'not-found', activeNav: '', articleSlug: null }
    }

    return { page: 'article', activeNav: article.page, articleSlug }
  }

  if (pageIds.has(normalizedHash)) {
    return { page: normalizedHash, activeNav: normalizedHash, articleSlug: null }
  }

  return { page: 'not-found', activeNav: '', articleSlug: null }
}

function getCarouselSlice(items, start, count) {
  return Array.from({ length: count }, (_, index) => {
    return items[(start + index) % items.length]
  })
}

function App() {
  const [route, setRoute] = useState(() => getRouteFromHash())
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [carouselStart, setCarouselStart] = useState(0)

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(getRouteFromHash())
    }

    window.addEventListener('hashchange', handleHashChange)

    return () => {
      window.removeEventListener('hashchange', handleHashChange)
    }
  }, [])

  const visibleWatchStories = getCarouselSlice(watchStories, carouselStart, 4)

  const changePage = (page) => {
    setIsSidebarOpen(false)

    if (typeof window === 'undefined') {
      setRoute({ page, activeNav: page, articleSlug: null })
      return
    }

    window.location.hash = page
  }

  const openArticle = (slug) => {
    setIsSidebarOpen(false)

    if (typeof window === 'undefined') {
      const article = getArticleBySlug(slug)
      setRoute({
        page: article ? 'article' : 'not-found',
        activeNav: article?.page ?? '',
        articleSlug: article?.slug ?? null,
      })
      return
    }

    window.location.hash = `materia/${slug}`
  }

  const showPreviousWatch = () => {
    setCarouselStart((current) => {
      return (current - 1 + watchStories.length) % watchStories.length
    })
  }

  const showNextWatch = () => {
    setCarouselStart((current) => {
      return (current + 1) % watchStories.length
    })
  }

  const currentArticle = route.articleSlug ? getArticleBySlug(route.articleSlug) : null

  const renderPage = () => {
    if (route.page === 'home') {
      return (
        <>
          <HomePage activeSection="Inicio" onChangePage={changePage} />

          <section className="news-grid-section">
            <div className="section-bar">
              <div>
                <p className="story-kicker">Pulso do portal</p>
                <h2>Ultimas do Nexus IA</h2>
              </div>
              <p>Blocos prontos para noticias reais, reviews, especiais e coberturas ao vivo.</p>
            </div>

            <div className="news-grid">
              {latestStories.map((story) => (
                <article className="news-card" key={story.headline}>
                  <p className="story-kicker">{story.category}</p>
                  <h3>{story.headline}</h3>
                  <p>{story.excerpt}</p>
                </article>
              ))}
            </div>
          </section>

          <WatchStrip
            stories={visibleWatchStories}
            onNext={showNextWatch}
            onPrevious={showPreviousWatch}
          />
        </>
      )
    }

    if (route.page === 'article' && currentArticle) {
      return (
        <ArticlePage
          article={currentArticle}
          relatedArticles={getRelatedArticles(currentArticle)}
          onChangePage={changePage}
          onOpenArticle={openArticle}
        />
      )
    }

    if (route.page === 'register') return <RegisterPage onChangePage={changePage} />
    if (route.page === 'login') return <LoginPage onChangePage={changePage} />
    if (route.page === 'not-found') return <NotFoundPage onChangePage={changePage} />
    if (route.page === 'noticias') return <NoticiasPage onOpenArticle={openArticle} />
    if (route.page === 'negocios') return <NegociosPage onOpenArticle={openArticle} />
    if (route.page === 'tecnologia') return <TecnologiaPage onOpenArticle={openArticle} />
    if (route.page === 'saude') return <SaudePage onOpenArticle={openArticle} />
    if (route.page === 'clima') return <ClimaPage onOpenArticle={openArticle} />
    if (route.page === 'cultura') return <CulturaPage onOpenArticle={openArticle} />
    if (route.page === 'politica') return <PoliticaPage onOpenArticle={openArticle} />
    if (route.page === 'ciencia') return <CienciaPage onOpenArticle={openArticle} />
    if (route.page === 'videos') return <VideosPage onOpenArticle={openArticle} />

    return <NotFoundPage onChangePage={changePage} />
  }

  return (
    <div className="app-shell">
      <Sidebar
        activePage={route.activeNav}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onChangePage={changePage}
      />

      <Header
        activePage={route.activeNav}
        onChangePage={changePage}
        onOpenMenu={() => setIsSidebarOpen(true)}
      />

      <main className="page-shell">{renderPage()}</main>

      <Footer onChangePage={changePage} />
    </div>
  )
}

export default App
