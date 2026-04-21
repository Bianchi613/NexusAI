import './watch-strip.css'

function WatchStrip({ onNext, onPrevious, onOpenArticle, stories }) {
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
          <button
            className="watch-card"
            key={story.slug ?? story.title}
            type="button"
            onClick={() => {
              if (story.slug && onOpenArticle) {
                onOpenArticle(story.slug)
              }
            }}
          >
            <div className="watch-thumb">
              <span className="watch-tag">{story.tag}</span>
              <span className="watch-stamp">Nexus AI</span>
            </div>
            <h3>{story.title}</h3>
            <p>{story.summary}</p>
          </button>
        ))}
      </div>
    </section>
  )
}

export default WatchStrip
