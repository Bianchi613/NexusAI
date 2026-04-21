import { useEffect, useState } from 'react'
import './styles/app-shell.css'
import ArticlePage from './components/article-page/index.jsx'
import Footer from './components/footer/index.jsx'
import Header from './components/header/index.jsx'
import Sidebar from './components/sidebar/index.jsx'
import { clearAccessToken, fetchCurrentUser, getStoredAccessToken } from './services/auth-api'
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
    if (!articleSlug) {
      return { page: 'not-found', activeNav: '', articleSlug: null }
    }

    return { page: 'article', activeNav: '', articleSlug }
  }

  if (pageIds.has(normalizedHash)) {
    return { page: normalizedHash, activeNav: normalizedHash, articleSlug: null }
  }

  return { page: 'not-found', activeNav: '', articleSlug: null }
}

function App() {
  const [route, setRoute] = useState(() => getRouteFromHash())
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(getRouteFromHash())
    }

    window.addEventListener('hashchange', handleHashChange)

    return () => {
      window.removeEventListener('hashchange', handleHashChange)
    }
  }, [])

  useEffect(() => {
    let isActive = true

    const loadSession = async () => {
      if (!getStoredAccessToken()) {
        return
      }

      try {
        const user = await fetchCurrentUser()
        if (isActive) {
          setCurrentUser(user)
        }
      } catch {
        if (isActive) {
          setCurrentUser(null)
        }
      }
    }

    loadSession()

    return () => {
      isActive = false
    }
  }, [])

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
      setRoute({
        page: slug ? 'article' : 'not-found',
        activeNav: '',
        articleSlug: slug ?? null,
      })
      return
    }

    window.location.hash = `materia/${slug}`
  }

  const handleAuthChange = (user) => {
    setCurrentUser(user ?? null)
  }

  const handleLogout = () => {
    clearAccessToken()
    setCurrentUser(null)
    changePage('home')
  }

  const renderPage = () => {
    if (route.page === 'home') {
      return <HomePage activeSection="Inicio" onChangePage={changePage} onOpenArticle={openArticle} />
    }

    if (route.page === 'article' && route.articleSlug) {
      return (
        <ArticlePage
          articleSlug={route.articleSlug}
          onChangePage={changePage}
          onOpenArticle={openArticle}
        />
      )
    }

    if (route.page === 'register') return <RegisterPage onAuthChange={handleAuthChange} onChangePage={changePage} />
    if (route.page === 'login') return <LoginPage onAuthChange={handleAuthChange} onChangePage={changePage} />
    if (route.page === 'not-found') return <NotFoundPage onChangePage={changePage} />
    if (route.page === 'noticias') return <NoticiasPage onChangePage={changePage} onOpenArticle={openArticle} />
    if (route.page === 'negocios') return <NegociosPage onChangePage={changePage} onOpenArticle={openArticle} />
    if (route.page === 'tecnologia') return <TecnologiaPage onChangePage={changePage} onOpenArticle={openArticle} />
    if (route.page === 'saude') return <SaudePage onChangePage={changePage} onOpenArticle={openArticle} />
    if (route.page === 'clima') return <ClimaPage onChangePage={changePage} onOpenArticle={openArticle} />
    if (route.page === 'cultura') return <CulturaPage onChangePage={changePage} onOpenArticle={openArticle} />
    if (route.page === 'politica') return <PoliticaPage onChangePage={changePage} onOpenArticle={openArticle} />
    if (route.page === 'ciencia') return <CienciaPage onChangePage={changePage} onOpenArticle={openArticle} />
    if (route.page === 'videos') return <VideosPage onChangePage={changePage} onOpenArticle={openArticle} />

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
        currentUser={currentUser}
        onChangePage={changePage}
        onLogout={handleLogout}
        onOpenMenu={() => setIsSidebarOpen(true)}
      />

      <main className="page-shell">{renderPage()}</main>

      <Footer onChangePage={changePage} />
    </div>
  )
}

export default App
