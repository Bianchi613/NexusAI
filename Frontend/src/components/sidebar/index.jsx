import './sidebar.css'
import { topSections } from '../../data/portalData'
import { mapSectionToPage } from '../../utils/navigation'

function Sidebar({ activePage, isOpen, onClose, onChangePage }) {
  return (
    <div className={isOpen ? 'sidebar-overlay is-open' : 'sidebar-overlay'} onClick={onClose}>
      <aside
        className={isOpen ? 'sidebar-panel is-open' : 'sidebar-panel'}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="sidebar-head">
          <button className="close-button" type="button" onClick={onClose} aria-label="Fechar menu">
            <span className="close-button__icon" aria-hidden="true"></span>
          </button>
        </div>

        <div className="sidebar-search">
          <input type="text" placeholder="Busque noticias, temas e mais" />
          <button type="button" aria-label="Buscar">
            <span className="sidebar-search__icon" aria-hidden="true"></span>
          </button>
        </div>

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
                  onClose()
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
