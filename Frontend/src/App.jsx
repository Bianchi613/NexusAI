import { useEffect, useState } from 'react'
import './styles/app-shell.css'
import Footer from './components/footer/index.jsx'
import Header from './components/header/index.jsx'
import Sidebar from './components/sidebar/index.jsx'
import WatchStrip from './components/watch-strip/index.jsx'
import { latestStories, watchStories } from './data/portalData'
import HomePage from './pages/home/index.jsx'
import LoginPage from './pages/login/index.jsx'
import RegisterPage from './pages/register/index.jsx'
import CulturaPage from './pages/cultura/index.jsx'

const pageIds = new Set([
  'home',
  'register',
  'login',
  'noticias',
  'negocios',
  'tecnologia',
  'saude',
  'cultura',
  'politica',
  'laboratorio-ia',
  'videos',
])

function getPageFromHash() {
  if (typeof window === 'undefined') {
    return 'home'
  }

  const hash = window.location.hash.replace('#', '').trim().toLowerCase()
  return pageIds.has(hash) ? hash : 'home'
}

function getCarouselSlice(items, start, count) {
  return Array.from({ length: count }, (_, index) => {
    return items[(start + index) % items.length]
  })
}

function PlaceholderPage({ title }) {
  return (
    <section>
      <p>EDITORIA</p>
      <h1>{title}</h1>
      <p>Pagina em construcao.</p>
    </section>
  )
}

function App() {
  const [activePage, setActivePage] = useState(() => getPageFromHash())
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [carouselStart, setCarouselStart] = useState(0)

  useEffect(() => {
    const handleHashChange = () => {
      setActivePage(getPageFromHash())
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
      setActivePage(page)
      return
    }

    window.location.hash = page
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

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onChangePage={changePage}
      />

      <Header
        activePage={activePage}
        onChangePage={changePage}
        onOpenMenu={() => setIsSidebarOpen(true)}
      />

      <main className="page-shell">
        {activePage === 'home' ? (
          <>
            <HomePage activeSection="Início" onChangePage={changePage} />

            <section className="news-grid-section">
              <div className="section-bar">
                <h2>Ultimas do Nexus IA</h2>
                <p>Blocos prontos para noticias reais, reviews e coberturas ao vivo.</p>
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
        ) : null}

        {activePage === 'register' ? <RegisterPage onChangePage={changePage} /> : null}
        {activePage === 'login' ? <LoginPage onChangePage={changePage} /> : null}
        {activePage === 'cultura' ? <CulturaPage /> : null}

        {activePage === 'noticias' ? <PlaceholderPage title="Notícias" /> : null}
        {activePage === 'negocios' ? <PlaceholderPage title="Negócios" /> : null}
        {activePage === 'tecnologia' ? <PlaceholderPage title="Tecnologia" /> : null}
        {activePage === 'saude' ? <PlaceholderPage title="Saúde" /> : null}
        {activePage === 'politica' ? <PlaceholderPage title="Política" /> : null}
        {activePage === 'laboratorio-ia' ? <PlaceholderPage title="Laboratório IA" /> : null}
        {activePage === 'videos' ? <PlaceholderPage title="Vídeos" /> : null}
      </main>

      <Footer onChangePage={changePage} />
    </div>
  )
}

export default App