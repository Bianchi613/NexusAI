import { useEffect, useState } from 'react'
import './styles/app-shell.css'
import ArticlePage from './components/article-page/index.jsx'
import Footer from './components/footer/index.jsx'
import Header from './components/header/index.jsx'
import Sidebar from './components/sidebar/index.jsx'
import { clearAccessToken, fetchCurrentUser, getStoredAccessToken } from './services/auth-api'
import AboutPage from './pages/about/index.jsx'
import CienciaPage from './pages/ciencia/index.jsx'
import ClimaPage from './pages/clima/index.jsx'
import ContactPage from './pages/contact/index.jsx'
import CulturaPage from './pages/cultura/index.jsx'
import HomePage from './pages/home/index.jsx'
import LoginPage from './pages/login/index.jsx'
import NegociosPage from './pages/negocios/index.jsx'
import NoticiasPage from './pages/noticias/index.jsx'
import NotFoundPage from './pages/not-found/index.jsx'
import PoliticaPage from './pages/politica/index.jsx'
import PrivacyPolicyPage from './pages/privacy-policy/index.jsx'
import RegisterPage from './pages/register/index.jsx'
import ReviewPage from './pages/review/index.jsx'
import SaudePage from './pages/saude/index.jsx'
import TecnologiaPage from './pages/tecnologia/index.jsx'
import TermsOfUsePage from './pages/terms-of-use/index.jsx'
import VideosPage from './pages/videos/index.jsx'

const pageIds = new Set([
  'about',
  'contato',
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
  'privacy-policy',
  'review',
  'terms-of-use',
  'videos',
])

const pageAliases = {
  about: 'about',
  ciencia: 'ciencia',
  clima: 'clima',
  contato: 'contato',
  cultura: 'cultura',
  home: 'home',
  inicio: 'home',
  login: 'login',
  negocios: 'negocios',
  'not-found': 'not-found',
  noticias: 'noticias',
  politica: 'politica',
  'politica-de-privacidade': 'privacy-policy',
  'privacy-policy': 'privacy-policy',
  register: 'register',
  review: 'review',
  saude: 'saude',
  'sobre-o-nexus-ia': 'about',
  tecnologia: 'tecnologia',
  'termos-de-uso': 'terms-of-use',
  'terms-of-use': 'terms-of-use',
  videos: 'videos',
}

function resolvePageId(page) {
  const normalizedPage = String(page ?? '').trim().toLowerCase()
  return pageAliases[normalizedPage] ?? null
}

function buildPageRoute(page) {
  const resolvedPage = resolvePageId(page)

  if (resolvedPage && pageIds.has(resolvedPage)) {
    return { page: resolvedPage, activeNav: resolvedPage, articleSlug: null }
  }

  return { page: 'not-found', activeNav: '', articleSlug: null }
}

function buildArticleRoute(slug) {
  if (!slug) {
    return { page: 'not-found', activeNav: '', articleSlug: null }
  }

  return {
    page: 'article',
    activeNav: '',
    articleSlug: slug,
  }
}

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

  const resolvedPage = resolvePageId(normalizedHash)
  if (resolvedPage && pageIds.has(resolvedPage)) {
    return { page: resolvedPage, activeNav: resolvedPage, articleSlug: null }
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

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
  }, [route.page, route.articleSlug])

  const changePage = (page) => {
    setIsSidebarOpen(false)
    const nextRoute = buildPageRoute(page)
    setRoute(nextRoute)

    if (typeof window === 'undefined') {
      return
    }

    window.location.hash = nextRoute.page
  }

  const openArticle = (slug) => {
    setIsSidebarOpen(false)
    const nextRoute = buildArticleRoute(slug)
    setRoute(nextRoute)

    if (typeof window === 'undefined') {
      return
    }

    window.location.hash = nextRoute.articleSlug
      ? `materia/${nextRoute.articleSlug}`
      : 'not-found'
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
    if (route.page === 'terms-of-use') return <TermsOfUsePage onChangePage={changePage} />
    if (route.page === 'privacy-policy') return <PrivacyPolicyPage onChangePage={changePage} />
    if (route.page === 'review') return <ReviewPage currentUser={currentUser} onChangePage={changePage} />
    if (route.page === 'contato') return <ContactPage onChangePage={changePage} />
    if (route.page === 'about') return <AboutPage onChangePage={changePage} />
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
        onOpenArticle={openArticle}
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
