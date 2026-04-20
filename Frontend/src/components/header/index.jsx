import './header.css'
import BrandWordmark from '../brand-wordmark/index.jsx'
import { topSections } from '../../data/portalData'

function Header({
  activePage,
  activeSection,
  onChangePage,
  onOpenMenu,
  onSelectSection,
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
          <button className="action-button" type="button" onClick={() => onChangePage('login')}>
            Entrar
          </button>
        </div>
      </div>

      <nav className="section-nav" aria-label="Secoes principais">
        {topSections.map((section) => (
          <button
            className={section === activeSection && activePage === 'home' ? 'nav-link is-active' : 'nav-link'}
            key={section}
            type="button"
            onClick={() => onSelectSection(section)}
          >
            {section}
          </button>
        ))}
      </nav>
    </header>
  )
}

export default Header
