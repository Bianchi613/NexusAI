import './info-page.css'

function InfoPage({ kicker, title, intro, sections, onChangePage }) {
  return (
    <article className="info-page">
      <header className="info-page__hero">
        <p className="story-kicker">{kicker}</p>
        <h1>{title}</h1>
        <p className="info-page__intro">{intro}</p>
      </header>

      <div className="info-page__sections">
        {sections.map((section) => (
          <section className="info-page__section" key={section.title}>
            <h2>{section.title}</h2>
            {section.paragraphs.map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
          </section>
        ))}
      </div>

      <div className="info-page__actions">
        <button className="primary-link" type="button" onClick={() => onChangePage('home')}>
          Voltar para a home
        </button>
      </div>
    </article>
  )
}

export default InfoPage
