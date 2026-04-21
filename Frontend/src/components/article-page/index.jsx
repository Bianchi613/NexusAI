import './article-page.css'

function ArticlePage({ article, relatedArticles, onChangePage, onOpenArticle }) {
  if (!article) {
    return null
  }

  return (
    <article className="article-page">
      <button
        className="text-link article-page__back"
        type="button"
        onClick={() => onChangePage(article.page)}
      >
        Voltar para {article.category}
      </button>

      <header className="article-page__lead">
        <p className="story-kicker">{article.category}</p>
        <h1>{article.title}</h1>
        <p className="article-page__summary">{article.summary}</p>

        <div className="article-page__meta">
          <span>{article.author}</span>
          <span>{article.publishedAt}</span>
          <span>{article.readTime}</span>
          <span>{article.location}</span>
        </div>
      </header>

      <div className="article-page__hero">
        <div className="article-page__hero-mark">
          <span>{article.label}</span>
          <strong>{article.category}</strong>
        </div>
        <p>
          Template fixo de materia pronto para renderizar o conteudo vindo do banco
          com metadados, corpo, tags e relacoes entre artigos.
        </p>
      </div>

      <div className="article-page__grid">
        <div className="article-page__body">
          {article.body.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>

        <aside className="article-page__rail">
          <section className="article-page__rail-section">
            <p className="article-page__label">Tags</p>
            <div className="article-page__tags">
              {article.tags.map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>
          </section>

          <section className="article-page__rail-section">
            <p className="article-page__label">Mais da editoria</p>
            <div className="article-page__related">
              {relatedArticles.map((item) => (
                <button
                  className="article-page__related-card"
                  key={item.slug}
                  type="button"
                  onClick={() => onOpenArticle(item.slug)}
                >
                  <span className="story-kicker">{item.label}</span>
                  <h3>{item.title}</h3>
                  <p>{item.excerpt}</p>
                </button>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </article>
  )
}

export default ArticlePage
