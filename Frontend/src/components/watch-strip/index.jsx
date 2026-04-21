import './watch-strip.css'

function WatchStrip({ onNext, onPrevious, stories }) {
  return (
    <section className="watch-strip">
      <div className="watch-head">
        <h2>Mais noticias</h2>
        <div className="watch-controls">
          <button type="button" onClick={onPrevious} aria-label="Ver noticias anteriores">
            &lt;
          </button>
          <button type="button" onClick={onNext} aria-label="Ver proximas noticias">
            &gt;
          </button>
        </div>
      </div>

      <div className="watch-track">
        {stories.map((story) => (
          <article className="watch-card" key={story.title}>
            <div className="watch-thumb">
              <span className="watch-tag">{story.tag}</span>
              <span className="watch-stamp">Nexus AI</span>
            </div>
            <h3>{story.title}</h3>
            <p>{story.summary}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

export default WatchStrip
