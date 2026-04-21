import { useEffect, useState } from 'react'
import NotFoundPage from '../../pages/not-found/index.jsx'
import { ApiError, fetchArticlePage } from '../../services/portal-api'
import { resolveVideoEmbed } from '../../utils/video-embed'
import './article-page.css'

function ArticlePage({ articleSlug, onChangePage, onOpenArticle }) {
  const [article, setArticle] = useState(null)
  const [status, setStatus] = useState('loading')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let isActive = true

    const loadArticle = async () => {
      setStatus('loading')
      setErrorMessage('')

      try {
        const data = await fetchArticlePage(articleSlug)
        if (!isActive) {
          return
        }
        setArticle(data)
        setStatus('success')
      } catch (error) {
        if (!isActive) {
          return
        }
        setStatus('error')
        setErrorMessage(
          error instanceof ApiError
            ? error.message
            : 'Nao foi possivel carregar a materia.',
        )
      }
    }

    loadArticle()

    return () => {
      isActive = false
    }
  }, [articleSlug])

  if (status === 'loading') {
    return (
      <section className="editorial-placeholder">
        <p className="story-kicker">Carregando materia</p>
        <h1>Buscando o conteudo dinamico dessa pagina.</h1>
        <p>O corpo da materia sera renderizado assim que o backend devolver o artigo publicado.</p>
      </section>
    )
  }

  if (status === 'error') {
    if (errorMessage.toLowerCase().includes('nao encontrado')) {
      return (
        <NotFoundPage
          onChangePage={onChangePage}
          kicker="Materia indisponivel"
          title="Essa materia nao existe mais."
          description="O link pode estar quebrado, o slug pode ser invalido ou a materia ainda nao foi publicada no portal."
        />
      )
    }

    return (
      <section className="editorial-placeholder">
        <p className="story-kicker">Materia indisponivel</p>
        <h1>Nao foi possivel carregar essa leitura.</h1>
        <p>{errorMessage}</p>
      </section>
    )
  }

  const videoEmbed = article.videoUrl ? resolveVideoEmbed(article.videoUrl) : null

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

      <div className={`article-page__hero${article.imageUrl ? '' : ' article-page__hero--without-image'}`}>
        {article.imageUrl ? (
          <div className="article-page__hero-media">
            <img src={article.imageUrl} alt={article.title} />
          </div>
        ) : null}

        <div className="article-page__hero-copy">
          <div className="article-page__hero-mark">
            <span>{article.label}</span>
            <strong>{article.category}</strong>
          </div>
          <p>
            Materia dinamica renderizada com imagem, metadados, corpo, tags e relacoes
            entre artigos publicados no banco.
          </p>
        </div>
      </div>

      {videoEmbed ? (
        <section className="article-page__video">
          <div className="article-page__video-head">
            <p className="story-kicker">Video relacionado</p>
            <h2>Assistir na plataforma</h2>
          </div>

          {videoEmbed.kind === 'iframe' ? (
            <div className="article-page__video-frame">
              <iframe
                src={videoEmbed.embedUrl}
                title={videoEmbed.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          ) : null}

          {videoEmbed.kind === 'direct' ? (
            <div className="article-page__video-frame">
              <video controls preload="metadata" src={videoEmbed.embedUrl}>
                Seu navegador nao conseguiu reproduzir este video.
              </video>
            </div>
          ) : null}

          {videoEmbed.kind === 'external' ? (
            <div className="article-page__video-fallback">
              <p>Este link de video nao aceita incorporacao direta no portal.</p>
              <a
                className="primary-link article-page__video-link"
                href={videoEmbed.originalUrl}
                target="_blank"
                rel="noreferrer"
              >
                Abrir video
              </a>
            </div>
          ) : null}
        </section>
      ) : null}

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
              {article.relatedArticles.map((item) => (
                <button
                  className="article-page__related-card"
                  key={item.slug}
                  type="button"
                  onClick={() => onOpenArticle(item.slug)}
                >
                  {item.imageUrl ? (
                    <div className="article-page__related-media">
                      <img src={item.imageUrl} alt={item.title} />
                    </div>
                  ) : null}
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
