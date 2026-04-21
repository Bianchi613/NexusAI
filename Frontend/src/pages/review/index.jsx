import { useEffect, useState } from 'react'
import './review.css'
import { ApiError } from '../../services/portal-api'
import {
  approveReviewArticle,
  createReviewArticle,
  createReviewCategory,
  createReviewTag,
  deleteReviewArticle,
  deleteReviewCategory,
  deleteReviewTag,
  getReviewArticle,
  listPendingReviewArticles,
  listReviewArticles,
  listReviewCategories,
  listReviewTags,
  rejectReviewArticle,
  updateReviewArticle,
  updateReviewCategory,
  updateReviewTag,
} from '../../services/review-api'

const ARTICLE_STATUS_OPTIONS = [
  { value: 'nao_revisada', label: 'Nao revisada' },
  { value: 'publicada', label: 'Publicada' },
  { value: 'rejeitada', label: 'Rejeitada' },
]

const ARTICLE_FILTER_OPTIONS = [
  { value: 'nao_revisada', label: 'Pendentes' },
  { value: 'publicada', label: 'Publicadas' },
  { value: 'rejeitada', label: 'Rejeitadas' },
  { value: 'all', label: 'Todas' },
]

function formatPortalDate(value) {
  if (!value) {
    return 'Ainda nao registrado'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Data indisponivel'
  }

  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Sao_Paulo',
  }).format(date)
}

function parseIdList(value = '') {
  return Array.from(
    new Set(
      String(value)
        .split(',')
        .map((item) => Number(item.trim()))
        .filter((item) => Number.isInteger(item) && item > 0),
    ),
  )
}

function formatIdList(items = []) {
  return Array.isArray(items) ? items.join(', ') : ''
}

function parseLineList(value = '') {
  return String(value)
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

function formatLineList(items = []) {
  return Array.isArray(items) ? items.join('\n') : ''
}

function buildEmptyArticleForm() {
  return {
    title: '',
    summary: '',
    body: '',
    categoryId: '',
    status: 'nao_revisada',
    aiModel: '',
    promptVersion: '',
    tagIds: '',
    imageUrls: '',
    videoUrls: '',
    sourceIds: '',
  }
}

function buildArticleForm(article) {
  if (!article) {
    return buildEmptyArticleForm()
  }

  return {
    title: article.title ?? '',
    summary: article.summary ?? '',
    body: article.body ?? '',
    categoryId: article.category_id ? String(article.category_id) : '',
    status: article.status ?? 'nao_revisada',
    aiModel: article.ai_model ?? '',
    promptVersion: article.prompt_version ?? '',
    tagIds: formatIdList(article.tag_ids),
    imageUrls: formatLineList(article.image_urls),
    videoUrls: formatLineList(article.video_urls),
    sourceIds: formatIdList(article.source_ids),
  }
}

function buildEmptyReferenceForm() {
  return { id: null, name: '', slug: '' }
}

function getStatusBadgeClass(status) {
  if (status === 'publicada') {
    return 'review-badge is-published'
  }
  if (status === 'rejeitada') {
    return 'review-badge is-rejected'
  }
  return 'review-badge is-pending'
}

function ReviewPage({ currentUser, onChangePage }) {
  const reviewerId = currentUser?.user_id ?? null
  const isReviewer = currentUser?.role === 'revisor'

  const [activeTab, setActiveTab] = useState('articles')
  const [bootStatus, setBootStatus] = useState('idle')
  const [bootMessage, setBootMessage] = useState('')

  const [articleFilter, setArticleFilter] = useState('nao_revisada')
  const [pendingArticles, setPendingArticles] = useState([])
  const [articleItems, setArticleItems] = useState([])
  const [selectedArticleId, setSelectedArticleId] = useState(null)
  const [articleForm, setArticleForm] = useState(buildEmptyArticleForm())
  const [articleMeta, setArticleMeta] = useState(null)
  const [articleMessage, setArticleMessage] = useState('')
  const [articleMessageType, setArticleMessageType] = useState('success')
  const [articleDetailStatus, setArticleDetailStatus] = useState('idle')

  const [categories, setCategories] = useState([])
  const [categoryEditor, setCategoryEditor] = useState(buildEmptyReferenceForm())
  const [categoryMessage, setCategoryMessage] = useState('')
  const [categoryMessageType, setCategoryMessageType] = useState('success')

  const [tags, setTags] = useState([])
  const [tagEditor, setTagEditor] = useState(buildEmptyReferenceForm())
  const [tagMessage, setTagMessage] = useState('')
  const [tagMessageType, setTagMessageType] = useState('success')

  const showMessage = (setter, typeSetter, message, type = 'success') => {
    setter(message)
    typeSetter(type)
  }

  const resolveErrorMessage = (error, fallbackMessage) => {
    return error instanceof ApiError ? error.message : fallbackMessage
  }

  const loadReferenceData = async () => {
    const [categoryItems, tagItems] = await Promise.all([
      listReviewCategories(reviewerId),
      listReviewTags(reviewerId),
    ])
    setCategories(categoryItems)
    setTags(tagItems)
  }

  const loadArticleCollections = async () => {
    const [pendingItems, articles] = await Promise.all([
      listPendingReviewArticles(reviewerId, { limit: 8 }),
      listReviewArticles(reviewerId, {
        limit: 30,
        status: articleFilter === 'all' ? undefined : articleFilter,
      }),
    ])

    setPendingArticles(pendingItems)
    setArticleItems(articles)

    const selectedStillExists = articles.some((article) => article.id === selectedArticleId)
    if (selectedArticleId === null && articles.length > 0) {
      setSelectedArticleId(articles[0].id)
      return
    }

    if (!selectedStillExists) {
      setSelectedArticleId(articles[0]?.id ?? null)
      if (articles.length === 0) {
        setArticleMeta(null)
        setArticleForm(buildEmptyArticleForm())
      }
    }
  }

  useEffect(() => {
    if (!reviewerId || !isReviewer) {
      return
    }

    let isActive = true

    const loadBootData = async () => {
      setBootStatus('loading')
      setBootMessage('')

      try {
        const [categoryItems, tagItems, pendingItems, articles] = await Promise.all([
          listReviewCategories(reviewerId),
          listReviewTags(reviewerId),
          listPendingReviewArticles(reviewerId, { limit: 8 }),
          listReviewArticles(reviewerId, { limit: 30, status: articleFilter }),
        ])

        if (!isActive) {
          return
        }

        setCategories(categoryItems)
        setTags(tagItems)
        setPendingArticles(pendingItems)
        setArticleItems(articles)
        setSelectedArticleId(articles[0]?.id ?? null)
        setBootStatus('success')
      } catch (error) {
        if (!isActive) {
          return
        }

        setBootStatus('error')
        setBootMessage(resolveErrorMessage(error, 'Nao foi possivel carregar o painel de revisao.'))
      }
    }

    loadBootData()

    return () => {
      isActive = false
    }
  }, [articleFilter, isReviewer, reviewerId])

  useEffect(() => {
    if (!reviewerId || !isReviewer || selectedArticleId === null) {
      return
    }

    let isActive = true

    const loadArticleDetail = async () => {
      setArticleDetailStatus('loading')
      setArticleMessage('')

      try {
        const article = await getReviewArticle(reviewerId, selectedArticleId)
        if (!isActive) {
          return
        }

        setArticleMeta(article)
        setArticleForm(buildArticleForm(article))
        setArticleDetailStatus('success')
      } catch (error) {
        if (!isActive) {
          return
        }

        setArticleDetailStatus('error')
        showMessage(
          setArticleMessage,
          setArticleMessageType,
          resolveErrorMessage(error, 'Nao foi possivel carregar a materia para revisao.'),
          'error',
        )
      }
    }

    loadArticleDetail()

    return () => {
      isActive = false
    }
  }, [isReviewer, reviewerId, selectedArticleId])

  const handleArticleFieldChange = (field) => (event) => {
    const nextValue = event.target.value
    setArticleForm((current) => ({
      ...current,
      [field]: nextValue,
    }))
  }

  const handleToggleTag = (tagId) => {
    setArticleForm((current) => {
      const currentIds = parseIdList(current.tagIds)
      const hasTag = currentIds.includes(tagId)
      const nextIds = hasTag
        ? currentIds.filter((item) => item !== tagId)
        : [...currentIds, tagId]

      return {
        ...current,
        tagIds: formatIdList(nextIds),
      }
    })
  }

  const handleNewArticle = () => {
    setSelectedArticleId(null)
    setArticleMeta(null)
    setArticleForm(buildEmptyArticleForm())
    setArticleMessage('')
    setArticleDetailStatus('idle')
  }

  const handleSaveArticle = async (event) => {
    event.preventDefault()

    try {
      const payload = {
        title: articleForm.title.trim(),
        summary: articleForm.summary.trim() || null,
        body: articleForm.body.trim(),
        category_id: articleForm.categoryId ? Number(articleForm.categoryId) : null,
        status: articleForm.status,
        ai_model: articleForm.aiModel.trim() || null,
        prompt_version: articleForm.promptVersion.trim() || null,
        tag_ids: parseIdList(articleForm.tagIds),
        image_urls: parseLineList(articleForm.imageUrls),
        video_urls: parseLineList(articleForm.videoUrls),
        source_ids: parseIdList(articleForm.sourceIds),
      }

      const article = selectedArticleId
        ? await updateReviewArticle(reviewerId, selectedArticleId, payload)
        : await createReviewArticle(reviewerId, payload)

      await loadArticleCollections()
      await loadReferenceData()
      setSelectedArticleId(article.id)
      showMessage(
        setArticleMessage,
        setArticleMessageType,
        selectedArticleId ? 'Materia atualizada com sucesso.' : 'Materia criada com sucesso.',
      )
    } catch (error) {
      showMessage(
        setArticleMessage,
        setArticleMessageType,
        resolveErrorMessage(error, 'Nao foi possivel salvar a materia.'),
        'error',
      )
    }
  }

  const handleApproveArticle = async () => {
    if (!selectedArticleId) {
      return
    }

    try {
      await approveReviewArticle(reviewerId, selectedArticleId)
      await loadArticleCollections()
      const article = await getReviewArticle(reviewerId, selectedArticleId)
      setArticleMeta(article)
      setArticleForm(buildArticleForm(article))
      showMessage(setArticleMessage, setArticleMessageType, 'Materia aprovada e publicada.')
    } catch (error) {
      showMessage(
        setArticleMessage,
        setArticleMessageType,
        resolveErrorMessage(error, 'Nao foi possivel aprovar a materia.'),
        'error',
      )
    }
  }

  const handleRejectArticle = async () => {
    if (!selectedArticleId) {
      return
    }

    try {
      await rejectReviewArticle(reviewerId, selectedArticleId)
      await loadArticleCollections()
      const article = await getReviewArticle(reviewerId, selectedArticleId)
      setArticleMeta(article)
      setArticleForm(buildArticleForm(article))
      showMessage(setArticleMessage, setArticleMessageType, 'Materia rejeitada com sucesso.')
    } catch (error) {
      showMessage(
        setArticleMessage,
        setArticleMessageType,
        resolveErrorMessage(error, 'Nao foi possivel rejeitar a materia.'),
        'error',
      )
    }
  }

  const handleDeleteArticle = async () => {
    if (!selectedArticleId) {
      return
    }

    const shouldDelete = window.confirm('Deseja mesmo apagar esta materia do painel de revisao?')
    if (!shouldDelete) {
      return
    }

    try {
      await deleteReviewArticle(reviewerId, selectedArticleId)
      setSelectedArticleId(null)
      setArticleMeta(null)
      setArticleForm(buildEmptyArticleForm())
      await loadArticleCollections()
      showMessage(setArticleMessage, setArticleMessageType, 'Materia removida com sucesso.')
    } catch (error) {
      showMessage(
        setArticleMessage,
        setArticleMessageType,
        resolveErrorMessage(error, 'Nao foi possivel apagar a materia.'),
        'error',
      )
    }
  }

  const handleCategorySelect = (category) => {
    setCategoryEditor({
      id: category.id,
      name: category.name,
      slug: category.slug,
    })
    setCategoryMessage('')
  }

  const handleTagSelect = (tag) => {
    setTagEditor({
      id: tag.id,
      name: tag.name,
      slug: tag.slug,
    })
    setTagMessage('')
  }

  const handleCategoryChange = (field) => (event) => {
    const nextValue = event.target.value
    setCategoryEditor((current) => ({
      ...current,
      [field]: nextValue,
    }))
  }

  const handleTagChange = (field) => (event) => {
    const nextValue = event.target.value
    setTagEditor((current) => ({
      ...current,
      [field]: nextValue,
    }))
  }

  const handleSaveCategory = async (event) => {
    event.preventDefault()

    try {
      const payload = {
        name: categoryEditor.name.trim(),
        slug: categoryEditor.slug.trim() || null,
      }

      const category = categoryEditor.id
        ? await updateReviewCategory(reviewerId, categoryEditor.id, payload)
        : await createReviewCategory(reviewerId, payload)

      const categoryItems = await listReviewCategories(reviewerId)
      setCategories(categoryItems)
      setCategoryEditor({
        id: category.id,
        name: category.name,
        slug: category.slug,
      })
      showMessage(
        setCategoryMessage,
        setCategoryMessageType,
        categoryEditor.id ? 'Categoria atualizada com sucesso.' : 'Categoria criada com sucesso.',
      )
    } catch (error) {
      showMessage(
        setCategoryMessage,
        setCategoryMessageType,
        resolveErrorMessage(error, 'Nao foi possivel salvar a categoria.'),
        'error',
      )
    }
  }

  const handleDeleteCategory = async () => {
    if (!categoryEditor.id) {
      return
    }

    const shouldDelete = window.confirm('Deseja mesmo apagar esta categoria?')
    if (!shouldDelete) {
      return
    }

    try {
      await deleteReviewCategory(reviewerId, categoryEditor.id)
      setCategories(await listReviewCategories(reviewerId))
      setCategoryEditor(buildEmptyReferenceForm())
      showMessage(setCategoryMessage, setCategoryMessageType, 'Categoria removida com sucesso.')
    } catch (error) {
      showMessage(
        setCategoryMessage,
        setCategoryMessageType,
        resolveErrorMessage(error, 'Nao foi possivel apagar a categoria.'),
        'error',
      )
    }
  }

  const handleSaveTag = async (event) => {
    event.preventDefault()

    try {
      const payload = {
        name: tagEditor.name.trim(),
        slug: tagEditor.slug.trim() || null,
      }

      const tag = tagEditor.id
        ? await updateReviewTag(reviewerId, tagEditor.id, payload)
        : await createReviewTag(reviewerId, payload)

      const tagItems = await listReviewTags(reviewerId)
      setTags(tagItems)
      setTagEditor({
        id: tag.id,
        name: tag.name,
        slug: tag.slug,
      })
      showMessage(
        setTagMessage,
        setTagMessageType,
        tagEditor.id ? 'Tag atualizada com sucesso.' : 'Tag criada com sucesso.',
      )
    } catch (error) {
      showMessage(
        setTagMessage,
        setTagMessageType,
        resolveErrorMessage(error, 'Nao foi possivel salvar a tag.'),
        'error',
      )
    }
  }

  const handleDeleteTag = async () => {
    if (!tagEditor.id) {
      return
    }

    const shouldDelete = window.confirm('Deseja mesmo apagar esta tag?')
    if (!shouldDelete) {
      return
    }

    try {
      await deleteReviewTag(reviewerId, tagEditor.id)
      setTags(await listReviewTags(reviewerId))
      setTagEditor(buildEmptyReferenceForm())
      showMessage(setTagMessage, setTagMessageType, 'Tag removida com sucesso.')
    } catch (error) {
      showMessage(
        setTagMessage,
        setTagMessageType,
        resolveErrorMessage(error, 'Nao foi possivel apagar a tag.'),
        'error',
      )
    }
  }

  if (!currentUser) {
    return (
      <section className="review-empty">
        <p className="story-kicker">Area restrita</p>
        <h1>Entre para acessar o frontend de revisao.</h1>
        <p>O painel editorial depende de autenticacao para carregar artigos, categorias e tags.</p>
        <div className="review-inline-actions">
          <button className="review-primary-button" type="button" onClick={() => onChangePage('login')}>
            Fazer login
          </button>
        </div>
      </section>
    )
  }

  if (!isReviewer) {
    return (
      <section className="review-empty">
        <p className="story-kicker">Acesso negado</p>
        <h1>Esta area esta disponivel apenas para revisores.</h1>
        <p>O usuario autenticado nao possui o papel necessario para aprovar, rejeitar ou editar o acervo editorial.</p>
        <div className="review-inline-actions">
          <button className="review-secondary-button" type="button" onClick={() => onChangePage('home')}>
            Voltar para a home
          </button>
        </div>
      </section>
    )
  }

  if (bootStatus === 'loading') {
    return (
      <section className="review-empty">
        <p className="story-kicker">Carregando revisao</p>
        <h1>Buscando o estado editorial do portal.</h1>
        <p>Assim que a API responder, o painel de revisao sera montado com artigos, categorias e tags.</p>
      </section>
    )
  }

  if (bootStatus === 'error') {
    return (
      <section className="review-empty">
        <p className="story-kicker">Painel indisponivel</p>
        <h1>Nao foi possivel carregar a area de revisao.</h1>
        <p>{bootMessage}</p>
      </section>
    )
  }

  return (
    <section className="review-page">
      <div className="review-page__hero">
        <p className="story-kicker">Operacao editorial</p>
        <h1>Frontend de revisao</h1>
        <p>
          Esta area conecta o frontend ao modulo `review` do backend para revisar artigos,
          editar categorias, manter tags e publicar o que realmente deve entrar no portal.
        </p>
      </div>

      <div className="review-page__tabs" role="tablist" aria-label="Secoes do painel">
        <button
          className={activeTab === 'articles' ? 'review-page__tab is-active' : 'review-page__tab'}
          type="button"
          onClick={() => setActiveTab('articles')}
        >
          Artigos
        </button>
        <button
          className={activeTab === 'categories' ? 'review-page__tab is-active' : 'review-page__tab'}
          type="button"
          onClick={() => setActiveTab('categories')}
        >
          Categorias
        </button>
        <button
          className={activeTab === 'tags' ? 'review-page__tab is-active' : 'review-page__tab'}
          type="button"
          onClick={() => setActiveTab('tags')}
        >
          Tags
        </button>
      </div>

      {activeTab === 'articles' ? (
        <div className="review-page__shell">
          <aside className="review-list">
            <div className="review-list__head">
              <div>
                <h2>Fila editorial</h2>
                <p>{pendingArticles.length} materias aguardando revisao imediata.</p>
              </div>
              <button className="review-secondary-button" type="button" onClick={handleNewArticle}>
                Nova materia
              </button>
            </div>

            <div className="review-list__filters">
              {ARTICLE_FILTER_OPTIONS.map((filterOption) => (
                <button
                  className={articleFilter === filterOption.value ? 'is-active' : ''}
                  key={filterOption.value}
                  type="button"
                  onClick={() => setArticleFilter(filterOption.value)}
                >
                  {filterOption.label}
                </button>
              ))}
            </div>

            {pendingArticles.length > 0 ? (
              <div className="review-reference__stack">
                {pendingArticles.map((article) => (
                  <button
                    className={selectedArticleId === article.id ? 'review-reference__item is-active' : 'review-reference__item'}
                    key={`pending-${article.id}`}
                    type="button"
                    onClick={() => setSelectedArticleId(article.id)}
                  >
                    <span className="story-kicker">Pendente</span>
                    <strong>{article.title}</strong>
                    <span>{article.category || 'Sem categoria'}</span>
                  </button>
                ))}
              </div>
            ) : null}

            <div className="review-list__stack">
              {articleItems.map((article) => (
                <button
                  className={selectedArticleId === article.id ? 'review-list__item is-active' : 'review-list__item'}
                  key={article.id}
                  type="button"
                  onClick={() => setSelectedArticleId(article.id)}
                >
                  <div className="review-badge-row">
                    <span className={getStatusBadgeClass(article.status)}>{article.status.replace('_', ' ')}</span>
                    {article.category ? <span className="review-badge">{article.category}</span> : null}
                  </div>
                  <strong>{article.title}</strong>
                  <p>{article.summary || 'Sem resumo editorial.'}</p>
                  <div className="review-list__meta">
                    <span>Criada em {formatPortalDate(article.created_at)}</span>
                    <span>{article.tag_ids.length} tags</span>
                  </div>
                </button>
              ))}
            </div>
          </aside>

          <section className="review-panel">
            <div className="review-panel__head">
              <div>
                <h2>{selectedArticleId ? 'Editar materia' : 'Nova materia'}</h2>
                <p>
                  Revise conteudo, status editorial, categoria, tags, imagens, videos e fontes
                  ligadas a cada materia gerada.
                </p>
              </div>
            </div>

            {articleMessage ? (
              <p className={articleMessageType === 'error' ? 'review-message is-error' : 'review-message is-success'}>
                {articleMessage}
              </p>
            ) : null}

            {articleMeta ? (
              <div className="review-form__meta">
                <span>ID {articleMeta.id}</span>
                <span>Criada em {formatPortalDate(articleMeta.created_at)}</span>
                <span>Revisada em {formatPortalDate(articleMeta.reviewed_at)}</span>
                <span>Publicada em {formatPortalDate(articleMeta.published_at)}</span>
              </div>
            ) : null}

            {selectedArticleId && articleDetailStatus === 'loading' ? (
              <p className="review-helper">Carregando detalhes da materia selecionada...</p>
            ) : null}

            <form className="review-form" onSubmit={handleSaveArticle}>
              <label>
                Titulo
                <input
                  type="text"
                  value={articleForm.title}
                  onChange={handleArticleFieldChange('title')}
                  required
                />
              </label>

              <label>
                Resumo
                <textarea
                  className="review-form__summary"
                  value={articleForm.summary}
                  onChange={handleArticleFieldChange('summary')}
                />
              </label>

              <label>
                Corpo da materia
                <textarea
                  className="review-form__body"
                  value={articleForm.body}
                  onChange={handleArticleFieldChange('body')}
                  required
                />
              </label>

              <div className="review-field-grid">
                <label>
                  Categoria
                  <select value={articleForm.categoryId} onChange={handleArticleFieldChange('categoryId')}>
                    <option value="">Sem categoria</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Status
                  <select value={articleForm.status} onChange={handleArticleFieldChange('status')}>
                    {ARTICLE_STATUS_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Modelo de IA
                  <input
                    type="text"
                    value={articleForm.aiModel}
                    onChange={handleArticleFieldChange('aiModel')}
                  />
                </label>

                <label>
                  Versao do prompt
                  <input
                    type="text"
                    value={articleForm.promptVersion}
                    onChange={handleArticleFieldChange('promptVersion')}
                  />
                </label>
              </div>

              <label>
                IDs das tags
                <input
                  type="text"
                  value={articleForm.tagIds}
                  onChange={handleArticleFieldChange('tagIds')}
                  placeholder="Ex.: 1, 4, 8"
                />
              </label>

              {tags.length > 0 ? (
                <div className="review-section">
                  <div className="review-section__head">
                    <div>
                      <h3>Atalhos de tags</h3>
                      <p>Clique para adicionar ou remover IDs no campo da materia.</p>
                    </div>
                  </div>
                  <div className="review-tag-toggle-row">
                    {tags.map((tag) => {
                      const currentTagIds = parseIdList(articleForm.tagIds)
                      const isActive = currentTagIds.includes(tag.id)

                      return (
                        <button
                          className={isActive ? 'review-tag-toggle is-active' : 'review-tag-toggle'}
                          key={tag.id}
                          type="button"
                          onClick={() => handleToggleTag(tag.id)}
                        >
                          {tag.name} #{tag.id}
                        </button>
                      )
                    })}
                  </div>
                </div>
              ) : null}

              <div className="review-field-grid">
                <label>
                  Imagens
                  <textarea
                    className="review-form__media"
                    value={articleForm.imageUrls}
                    onChange={handleArticleFieldChange('imageUrls')}
                    placeholder="Uma URL por linha"
                  />
                  <span className="review-field-hint">Cole aqui as URLs das imagens, uma por linha.</span>
                </label>

                <label>
                  Videos
                  <textarea
                    className="review-form__media"
                    value={articleForm.videoUrls}
                    onChange={handleArticleFieldChange('videoUrls')}
                    placeholder="Uma URL por linha"
                  />
                  <span className="review-field-hint">Cole aqui as URLs dos videos, uma por linha.</span>
                </label>
              </div>

              <label>
                IDs das fontes brutas
                <input
                  type="text"
                  value={articleForm.sourceIds}
                  onChange={handleArticleFieldChange('sourceIds')}
                  placeholder="Ex.: 12, 18, 19"
                />
              </label>

              <p className="review-helper">
                A aprovacao publica a materia. A rejeicao a remove da camada publica, mas mantem o registro editorial.
              </p>

              <div className="review-form__actions">
                <button className="review-primary-button" type="submit">
                  {selectedArticleId ? 'Salvar alteracoes' : 'Criar materia'}
                </button>
                {selectedArticleId ? (
                  <>
                    <button className="review-secondary-button" type="button" onClick={handleApproveArticle}>
                      Aprovar e publicar
                    </button>
                    <button className="review-secondary-button" type="button" onClick={handleRejectArticle}>
                      Rejeitar
                    </button>
                    <button className="review-danger-button" type="button" onClick={handleDeleteArticle}>
                      Apagar
                    </button>
                  </>
                ) : null}
              </div>
            </form>
          </section>
        </div>
      ) : null}

      {activeTab === 'categories' ? (
        <div className="review-reference">
          <aside className="review-list">
            <div className="review-list__head">
              <div>
                <h2>Categorias</h2>
                <p>Mantenha a taxonomia editorial usada pelo painel e pela camada publica.</p>
              </div>
              <button
                className="review-secondary-button"
                type="button"
                onClick={() => setCategoryEditor(buildEmptyReferenceForm())}
              >
                Nova categoria
              </button>
            </div>

            <div className="review-reference__stack">
              {categories.map((category) => (
                <button
                  className={categoryEditor.id === category.id ? 'review-reference__item is-active' : 'review-reference__item'}
                  key={category.id}
                  type="button"
                  onClick={() => handleCategorySelect(category)}
                >
                  <strong>{category.name}</strong>
                  <span>{category.slug}</span>
                </button>
              ))}
            </div>
          </aside>

          <section className="review-panel">
            <div className="review-panel__head">
              <div>
                <h2>{categoryEditor.id ? 'Editar categoria' : 'Nova categoria'}</h2>
                <p>As alteracoes aqui impactam a camada editorial e a classificacao das materias.</p>
              </div>
            </div>

            {categoryMessage ? (
              <p className={categoryMessageType === 'error' ? 'review-message is-error' : 'review-message is-success'}>
                {categoryMessage}
              </p>
            ) : null}

            <form className="review-reference__editor" onSubmit={handleSaveCategory}>
              <label>
                Nome
                <input type="text" value={categoryEditor.name} onChange={handleCategoryChange('name')} required />
              </label>

              <label>
                Slug
                <input type="text" value={categoryEditor.slug} onChange={handleCategoryChange('slug')} />
              </label>

              <p className="review-reference__hint">
                Exemplo de uso: o portal pode exibir uma categoria com nome visual diferente do slug salvo.
              </p>

              <div className="review-reference__actions">
                <button className="review-primary-button" type="submit">
                  {categoryEditor.id ? 'Salvar categoria' : 'Criar categoria'}
                </button>
                {categoryEditor.id ? (
                  <button className="review-danger-button" type="button" onClick={handleDeleteCategory}>
                    Apagar categoria
                  </button>
                ) : null}
              </div>
            </form>
          </section>
        </div>
      ) : null}

      {activeTab === 'tags' ? (
        <div className="review-reference">
          <aside className="review-list">
            <div className="review-list__head">
              <div>
                <h2>Tags</h2>
                <p>Gerencie os marcadores usados para organizar e relacionar as materias.</p>
              </div>
              <button
                className="review-secondary-button"
                type="button"
                onClick={() => setTagEditor(buildEmptyReferenceForm())}
              >
                Nova tag
              </button>
            </div>

            <div className="review-reference__stack">
              {tags.map((tag) => (
                <button
                  className={tagEditor.id === tag.id ? 'review-reference__item is-active' : 'review-reference__item'}
                  key={tag.id}
                  type="button"
                  onClick={() => handleTagSelect(tag)}
                >
                  <strong>{tag.name}</strong>
                  <span>{tag.slug}</span>
                </button>
              ))}
            </div>
          </aside>

          <section className="review-panel">
            <div className="review-panel__head">
              <div>
                <h2>{tagEditor.id ? 'Editar tag' : 'Nova tag'}</h2>
                <p>As tags ajudam a conectar materias, destacar temas e alimentar a camada publica de leitura.</p>
              </div>
            </div>

            {tagMessage ? (
              <p className={tagMessageType === 'error' ? 'review-message is-error' : 'review-message is-success'}>
                {tagMessage}
              </p>
            ) : null}

            <form className="review-reference__editor" onSubmit={handleSaveTag}>
              <label>
                Nome
                <input type="text" value={tagEditor.name} onChange={handleTagChange('name')} required />
              </label>

              <label>
                Slug
                <input type="text" value={tagEditor.slug} onChange={handleTagChange('slug')} />
              </label>

              <div className="review-reference__actions">
                <button className="review-primary-button" type="submit">
                  {tagEditor.id ? 'Salvar tag' : 'Criar tag'}
                </button>
                {tagEditor.id ? (
                  <button className="review-danger-button" type="button" onClick={handleDeleteTag}>
                    Apagar tag
                  </button>
                ) : null}
              </div>
            </form>
          </section>
        </div>
      ) : null}
    </section>
  )
}

export default ReviewPage
