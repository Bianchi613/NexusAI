import './footer.css'
import BrandWordmark from '../brand-wordmark/index.jsx'
import { footerSections } from '../../data/portalData'

const socialLinks = [
  {
    label: 'X',
    icon: (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M4 4L20 20M20 4L4 20"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
  {
    label: 'Facebook',
    icon: (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M13.5 21V13.2H16.3L16.7 10.2H13.5V8.3C13.5 7.4 14 6.6 15.5 6.6H16.8V4C16 3.9 15.2 3.8 14.4 3.8C11.9 3.8 10.3 5.3 10.3 8.1V10.2H7.8V13.2H10.3V21H13.5Z"
          fill="currentColor"
        />
      </svg>
    ),
  },
  {
    label: 'Instagram',
    icon: (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="4.5" y="4.5" width="15" height="15" rx="4" fill="none" stroke="currentColor" strokeWidth="2" />
        <circle cx="12" cy="12" r="3.5" fill="none" stroke="currentColor" strokeWidth="2" />
        <circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" />
      </svg>
    ),
  },
  {
    label: 'TikTok',
    icon: (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M14 4V13.2C14 15 12.6 16.4 10.8 16.4C9.3 16.4 8 15.1 8 13.6C8 12.1 9.3 10.8 10.8 10.8C11.2 10.8 11.5 10.9 11.9 11V8.1C11.5 8 11.2 8 10.8 8C7.8 8 5.4 10.4 5.4 13.4C5.4 16.5 7.8 18.8 10.8 18.8C13.9 18.8 16.3 16.4 16.3 13.4V9.2C17.4 10.1 18.8 10.6 20.3 10.7V7.9C18.2 7.7 16.4 6.1 16 4H14Z"
          fill="currentColor"
        />
      </svg>
    ),
  },
  {
    label: 'LinkedIn',
    icon: (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M6.4 8.5C7.5 8.5 8.3 7.7 8.3 6.6C8.3 5.5 7.5 4.7 6.4 4.7C5.3 4.7 4.5 5.5 4.5 6.6C4.5 7.7 5.3 8.5 6.4 8.5ZM4.8 10H8V19.3H4.8V10ZM10 10H13.1V11.3H13.2C13.6 10.5 14.8 9.7 16.4 9.7C19.7 9.7 20.3 11.9 20.3 14.7V19.3H17.1V15.2C17.1 14.2 17.1 12.9 15.7 12.9C14.2 12.9 14 14 14 15.1V19.3H10.8V10H10Z"
          fill="currentColor"
        />
      </svg>
    ),
  },
  {
    label: 'YouTube',
    icon: (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M20.6 8.2C20.4 7.4 19.8 6.8 19 6.6C17.6 6.2 12 6.2 12 6.2C12 6.2 6.4 6.2 5 6.6C4.2 6.8 3.6 7.4 3.4 8.2C3 9.6 3 12.5 3 12.5C3 12.5 3 15.4 3.4 16.8C3.6 17.6 4.2 18.2 5 18.4C6.4 18.8 12 18.8 12 18.8C12 18.8 17.6 18.8 19 18.4C19.8 18.2 20.4 17.6 20.6 16.8C21 15.4 21 12.5 21 12.5C21 12.5 21 9.6 20.6 8.2ZM10.2 15.1V9.9L14.8 12.5L10.2 15.1Z"
          fill="currentColor"
        />
      </svg>
    ),
  },
]

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

function Footer({ onChangePage }) {
  return (
    <footer className="site-footer">
      <div className="footer-brand">
        <BrandWordmark className="brand-wordmark--footer" />
      </div>

      <nav className="footer-nav" aria-label="Mapa do portal">
        {footerSections.map((section) => (
          <a
            href="/"
            key={section}
            onClick={(event) => {
              event.preventDefault()
              onChangePage(mapSectionToPage(section))
            }}
          >
            {section}
          </a>
        ))}
      </nav>

      <div className="social-row">
        <span>Siga o Nexus IA em:</span>
        <div className="social-icons" aria-label="Redes sociais do Nexus IA">
          {socialLinks.map((item) => (
            <a href="/" key={item.label} aria-label={item.label} onClick={(event) => event.preventDefault()}>
              {item.icon}
            </a>
          ))}
        </div>
      </div>

      <div className="footer-links">
        <a href="/" onClick={(event) => event.preventDefault()}>
          Termos de uso
        </a>
        <a href="/" onClick={(event) => event.preventDefault()}>
          Politica de privacidade
        </a>
        <a href="/" onClick={(event) => event.preventDefault()}>
          Acessibilidade
        </a>
        <a href="/" onClick={(event) => event.preventDefault()}>
          Contato
        </a>
        <a href="/" onClick={(event) => event.preventDefault()}>
          Sobre o Nexus IA
        </a>
      </div>

      <p className="copyright">
        Copyright 2026 Nexus IA. Todos os direitos reservados. O Nexus IA e uma
        plataforma brasileira de noticias com fluxo editorial apoiado por inteligencia artificial.
      </p>
    </footer>
  )
}

export default Footer