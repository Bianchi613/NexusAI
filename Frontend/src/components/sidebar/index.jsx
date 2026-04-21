import { useEffect, useState } from 'react'
import './sidebar.css'
import { topSections } from '../../data/portalData'
import { ApiError, searchPublishedArticles } from '../../services/portal-api'
import { mapSectionToPage } from '../../utils/navigation'

function normalizeSearchValue(value = '') {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
}

function Sidebar({ activePage, isOpen, onClose, onChangePage, onOpenArticle }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [status, setStatus] = useState('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const normalizedQuery = normalizeSearchValue(query)
  const hasQuery = normalizedQuery.length >= 2

  useEffect(() => {
    let isActive = true

    if (!isOpen || !hasQuery) {
      return undefined
    }

    const timeoutId = window.setTimeout(async () => {
      setStatus('loading')
      setErrorMessage('')

      try {
        const data = await searchPublishedArticles(query, { limit: 6 })

        if (!isActive) {
          return
        }

        setResults(data.items)
        setStatus('success')
      } catch (error) {
        if (!isActive) {
          return
        }

        setResults([])
        setStatus('error')
        setErrorMessage(
          error instanceof ApiError
            ? error.message
            : 'Não foi possível carregar as matérias para a busca.',
        )
      }
    }, 220)

    return () => {
      isActive = false
      window.clearTimeout(timeoutId)
    }
  }, [hasQuery, isOpen, query])

  const handleClose = () => {
    setQuery('')
    setResults([])
    setStatus('idle')
    setErrorMessage('')
    onClose()
  }

  const handleQueryChange = (event) => {
    const nextValue = event.target.value
    setQuery(nextValue)

    if (normalizeSearchValue(nextValue).length < 2) {
      setResults([])
      setStatus('idle')
      setErrorMessage('')
    }
  }

  const handleSearchSubmit = (event) => {
    event.preventDefault()

    if (results.length > 0 && onOpenArticle) {
      onOpenArticle(results[0].slug)
      handleClose()
    }
  }

  return (
    <div
      className={isOpen ? 'sidebar-overlay is-open' : 'sidebar-overlay'}
      onClick={handleClose}
    >
      <aside
        className={isOpen ? 'sidebar-panel is-open' : 'sidebar-panel'}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="sidebar-head">
          <button
            className="close-button"
            type="button"
            onClick={handleClose}
            aria-label="Fechar menu"
          >
            <span className="close-button__icon" aria-hidden="true"></span>
          </button>
        </div>

        <form className="sidebar-search" onSubmit={handleSearchSubmit}>
          <input
            type="text"
            value={query}
            placeholder="Busque notícias, temas e mais"
            onChange={handleQueryChange}
          />
          <button type="submit" aria-label="Buscar" disabled={status === 'loading'}>
            <span className="sidebar-search__icon" aria-hidden="true"></span>
          </button>
        </form>

        {hasQuery && status === 'loading' ? (
          <p className="sidebar-search-feedback">Buscando matérias...</p>
        ) : null}

        {hasQuery && status === 'error' ? (
          <p className="sidebar-search-feedback">{errorMessage}</p>
        ) : null}

        {hasQuery && status === 'success' && results.length === 0 ? (
          <p className="sidebar-search-feedback">
            Nenhuma matéria encontrada para essa busca.
          </p>
        ) : null}

        {results.length > 0 ? (
          <div className="sidebar-search-results">
            {results.map((article) => (
              <button
                className="sidebar-search-result"
                key={article.slug}
                type="button"
                onClick={() => {
                  if (onOpenArticle) {
                    onOpenArticle(article.slug)
                  }
                  handleClose()
                }}
              >
                <span className="story-kicker">{article.category}</span>
                <strong>{article.title}</strong>
                <p>{article.excerpt || article.summary}</p>
              </button>
            ))}
          </div>
        ) : null}

        <div className="sidebar-groups">
          {topSections.map((section) => {
            const page = mapSectionToPage(section)
            const isActive = activePage === page

            return (
              <button
                className={isActive ? 'sidebar-link is-active' : 'sidebar-link'}
                key={section}
                type="button"
                onClick={() => {
                  onChangePage(page)
                  handleClose()
                }}
              >
                <span>{section}</span>
                <span className="sidebar-arrow" aria-hidden="true">
                  &gt;
                </span>
              </button>
            )
          })}
        </div>
      </aside>
    </div>
  )
}

export default Sidebar
