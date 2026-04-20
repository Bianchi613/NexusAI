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
          <p className="story-kicker">{activeSection}</p>
          <h1>
            Nexus IA monta uma home de noticias com cara de portal editorial e
            espaco real para cadastro, login e leitura diaria.
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
            <span>Atualizado agora</span>
            <span>Redacao Nexus IA</span>
          </div>
        </article>

        <aside className="hero-rail">
          <div className="hero-visual">
            <div className="hero-visual-mark">
              <img src={mark} alt="" />
            </div>
            <div className="hero-visual-copy">
              <p className="story-kicker">Visao da plataforma</p>
              <h2>Mais proximo de uma capa editorial do que de uma landing generica.</h2>
            </div>
          </div>

          <div className="rail-panel">
            <div className="rail-panel-head">
              <h3>Mais lidas</h3>
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
          </article>
        ))}
      </div>
    </section>
  )
}

export default HomePage
