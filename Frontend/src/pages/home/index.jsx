import './home.css'
import mark from '../../../logos/Icon_Nexus_1.png'
import { mostRead, sectionSummaries, sideStories } from '../../data/portalData'

function HomePage({ activeSection, onChangePage }) {
  const sectionSummary = sectionSummaries[activeSection] ?? sectionSummaries.Home
  const summary = sectionSummary ?? sectionSummaries.Inicio

  return (
    <section className="home-page">
      <div className="hero-grid">
        <article className="hero-main">
          <div className="hero-label-row">
            <p className="story-kicker">{activeSection}</p>
            <span className="hero-live-pill">Edicao ao vivo</span>
          </div>

          <h1>
            Nexus IA monta uma home com peso de portal editorial e caminho claro para cadastro,
            login e leitura diaria.
          </h1>
          <p className="hero-summary">{summary}</p>

          <div className="hero-actions">
            <button className="primary-link" type="button" onClick={() => onChangePage('register')}>
              Criar conta
            </button>
            <button className="text-link" type="button" onClick={() => onChangePage('login')}>
              Fazer login
            </button>
          </div>

          <div className="hero-meta">
            <span>Atualizado ha poucos minutos</span>
            <span>Redacao Nexus IA</span>
            <span>Briefing continuo</span>
          </div>

          <div className="hero-metrics">
            <div>
              <strong>24/7</strong>
              <span>Monitoramento de sinais</span>
            </div>
            <div>
              <strong>09</strong>
              <span>Editorias ja mapeadas</span>
            </div>
            <div>
              <strong>01</strong>
              <span>Fluxo unificado de conta e leitura</span>
            </div>
          </div>
        </article>

        <aside className="hero-rail">
          <div className="hero-visual">
            <div className="hero-visual-mark">
              <img src={mark} alt="" />
            </div>
            <div className="hero-visual-copy">
              <p className="story-kicker">Visao da plataforma</p>
              <h2>Mais proximo de uma capa de jornal digital do que de uma landing generica.</h2>
              <p>
                A primeira dobra organiza hierarquia, ritmo e contraste para que as noticias
                ocupem o centro da experiencia.
              </p>
            </div>
          </div>

          <div className="rail-panel">
            <div className="rail-panel-head">
              <h3>Mais lidas</h3>
              <p>Leitura recorrente com mais peso editorial.</p>
            </div>
            <ol className="most-read-list">
              {mostRead.map((story) => (
                <li key={story}>{story}</li>
              ))}
            </ol>
          </div>
        </aside>
      </div>

      <div className="secondary-grid">
        {sideStories.map((story) => (
          <article className="secondary-story" key={story.title}>
            <p className="story-kicker">{story.label}</p>
            <h2>{story.title}</h2>
            <p>{story.summary}</p>
            <span className="secondary-story__link">Continuar leitura</span>
          </article>
        ))}
      </div>
    </section>
  )
}

export default HomePage
