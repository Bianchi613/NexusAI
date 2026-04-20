import './header.css'
import BrandWordmark from '../brand-wordmark/index.jsx'
import { topSections } from '../../data/portalData'

function mapSectionToPage(section) {
  const normalized = section.trim().toLowerCase()

  if (normalized === 'início' || normalized === 'inicio') return 'home'
  if (normalized === 'notícias' || normalized === 'noticias') return 'noticias'
  if (normalized === 'negócios' || normalized === 'negocios') return 'negocios'
  if (normalized === 'tecnologia') return 'tecnologia'
  if (normalized === 'saúde' || normalized === 'saude') return 'saude'
  if (normalized === 'cultura') return 'cultura'
  if (normalized === 'política' || normalized === 'politica') return 'politica'
  if (normalized === 'laboratório ia' || normalized === 'laboratorio ia') return 'laboratorio-ia'
  if (normalized === 'vídeos' || normalized === 'videos') return 'videos'

  return 'home'
}

function Header({
  activePage,
  onChangePage,
  onOpenMenu,
}) {
  return (
    <header className="site-header">
      <div className="top-header">
        <div className="left-actions">
          <button
            className="menu-search-button"
            type="button"
            aria-label="Abrir menu e busca"
            onClick={onOpenMenu}
          >
            <span className="menu-search-button__menu" aria-hidden="true">
              <span></span>
              <span></span>
              <span></span>
            </span>
            <span className="menu-search-button__search" aria-hidden="true"></span>
          </button>
        </div>

        <button
          className="brand-lockup"
          type="button"
          onClick={() => onChangePage('home')}
          aria-label="Ir para a pagina inicial"
        >
          <BrandWordmark />
        </button>

        <div className="account-actions">
          <button
            className="action-button action-button-solid"
            type="button"
            onClick={() => onChangePage('register')}
          >
            Cadastre-se
          </button>
          <button
            className="action-button"
            type="button"
            onClick={() => onChangePage('login')}
          >
            Entrar
          </button>
        </div>
      </div>

      <nav className="section-nav" aria-label="Secoes principais">
        {topSections.map((section) => {
          const page = mapSectionToPage(section)
          const isActive = activePage === page

          return (
            <button
              className={isActive ? 'nav-link is-active' : 'nav-link'}
              key={section}
              type="button"
              onClick={() => onChangePage(page)}
            >
              {section}
            </button>
          )
        })}
      </nav>
    </header>
  )
}

export default Header