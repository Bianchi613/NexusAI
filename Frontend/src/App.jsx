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

const pageIds = new Set(['home', 'register', 'login'])

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

function App() {
  const [activePage, setActivePage] = useState(() => getPageFromHash())
  const [activeSection, setActiveSection] = useState('Inicio')
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

  const openSection = (section) => {
    setIsSidebarOpen(false)
    setActiveSection(section)
    changePage('home')
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
        activeSection={activeSection}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onChangePage={changePage}
        onSelectSection={openSection}
      />

      <Header
        activePage={activePage}
        activeSection={activeSection}
        onChangePage={changePage}
        onOpenMenu={() => setIsSidebarOpen(true)}
        onSelectSection={openSection}
      />

      <main className="page-shell">
        {activePage === 'home' ? (
          <HomePage activeSection={activeSection} onChangePage={changePage} />
        ) : null}
        {activePage === 'register' ? <RegisterPage onChangePage={changePage} /> : null}
        {activePage === 'login' ? <LoginPage onChangePage={changePage} /> : null}

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
      </main>

      <Footer />
    </div>
  )
}

export default App
