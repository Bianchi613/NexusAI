import { ApiError, request } from './api-client'

function formatPublishedAt(value) {
  if (!value) {
    return 'Atualizado agora'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Atualizado agora'
  }

  const formatter = new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Sao_Paulo',
  })

  return formatter.format(date).replace(/\./g, '')
}

function formatForecastDate(value) {
  if (!value) {
    return ''
  }

  const date = new Date(`${value}T12:00:00`)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    timeZone: 'America/Sao_Paulo',
  }).format(date).replace(/\./g, '')
}

function formatReadTime(value) {
  const minutes = Number(value)
  if (!Number.isFinite(minutes) || minutes <= 0) {
    return '1 min'
  }
  return `${minutes} min`
}

function mapArticleCard(article) {
  const category = article.category ?? null

  return {
    id: article.id,
    slug: article.slug,
    page: category?.slug ?? 'noticias',
    category: category?.name ?? 'Noticias',
    categorySlug: category?.slug ?? 'noticias',
    label: article.label ?? category?.name ?? 'Portal',
    title: article.title,
    summary: article.summary ?? article.excerpt ?? '',
    excerpt: article.excerpt ?? article.summary ?? '',
    author: article.author ?? 'Redacao Nexus IA',
    publishedAt: formatPublishedAt(article.published_at),
    readTime: formatReadTime(article.read_time_minutes),
    location: article.location ?? 'Brasil',
    imageUrl: article.image_url ?? null,
    videoUrl: article.video_url ?? null,
  }
}

function mapCategoryDetail(payload) {
  const articles = (payload.articles ?? []).map(mapArticleCard)
  const featuredArticle = payload.featured_article ? mapArticleCard(payload.featured_article) : articles[0] ?? null

  return {
    page: payload.category.slug,
    eyebrow: payload.category.name,
    title: payload.category.title ?? payload.category.name,
    description: payload.category.description ?? '',
    railTitle: payload.category.rail_title ?? 'Pontos da editoria',
    railItems: payload.category.rail_items ?? [],
    featuredArticle,
    articles,
    hasMore: payload.has_more ?? false,
  }
}

function mapArticleDetail(payload) {
  const category = payload.category ?? null
  const imageUrls = Array.isArray(payload.image_urls)
    ? payload.image_urls.filter(Boolean)
    : payload.image_url
      ? [payload.image_url]
      : []
  const videoUrls = Array.isArray(payload.video_urls)
    ? payload.video_urls.filter(Boolean)
    : payload.video_url
      ? [payload.video_url]
      : []

  return {
    id: payload.id,
    slug: payload.slug,
    page: category?.slug ?? 'noticias',
    category: category?.name ?? 'Noticias',
    categorySlug: category?.slug ?? 'noticias',
    label: payload.label ?? category?.name ?? 'Portal',
    title: payload.title,
    summary: payload.summary ?? '',
    author: payload.author ?? 'Redacao Nexus IA',
    publishedAt: formatPublishedAt(payload.published_at),
    readTime: formatReadTime(payload.read_time_minutes),
    location: payload.location ?? 'Brasil',
    imageUrl: imageUrls[0] ?? null,
    imageUrls,
    videoUrl: videoUrls[0] ?? null,
    videoUrls,
    body: payload.body_paragraphs ?? [],
    tags: (payload.tags ?? []).map((tag) => tag.name),
    sourceArticles: (payload.source_articles ?? []).map((sourceArticle) => ({
      rawArticleId: sourceArticle.raw_article_id,
      sourceName: sourceArticle.source_name ?? '',
      originalTitle: sourceArticle.original_title,
      originalUrl: sourceArticle.original_url,
      originalAuthor: sourceArticle.original_author ?? '',
    })),
    relatedArticles: (payload.related_articles ?? []).map(mapArticleCard),
  }
}

function mapHome(payload) {
  const latestArticles = (payload.latest_articles ?? []).map(mapArticleCard)
  const watchArticles = (payload.watch_articles ?? []).map((article) => ({
    ...mapArticleCard(article),
    tag: article.category?.name ?? article.label ?? 'Portal',
  }))
  const featuredCategories = (payload.featured_categories ?? []).map(mapCategoryDetail)

  return {
    heroArticle: latestArticles[0] ?? null,
    latestArticles,
    watchArticles,
    featuredCategories,
  }
}

function mapWeatherDay(day) {
  return {
    date: day.date,
    label: formatForecastDate(day.date),
    conditionCode: day.condition_code ?? null,
    condition: day.condition ?? 'Condicao indisponivel',
    minTempC: day.min_temp_c ?? null,
    maxTempC: day.max_temp_c ?? null,
    uvIndex: day.uv_index ?? null,
    rainProbability: day.rain_probability ?? null,
  }
}

function mapWeatherLocation(location) {
  const daily = (location.daily ?? []).map(mapWeatherDay)

  return {
    locationKey: location.location_key,
    city: location.city,
    stateCode: location.state_code,
    stateName: location.state_name ?? '',
    displayName: location.display_name,
    headline: location.headline,
    summary: location.summary,
    advisoryItems: location.advisory_items ?? [],
    sourceName: location.source_name,
    sourceUrl: location.source_url ?? null,
    updatedAt: formatPublishedAt(location.updated_at),
    daily,
    weekRange:
      daily.length > 0
        ? `${daily[0].label} - ${daily[Math.min(daily.length - 1, 6)].label}`
        : 'Semana atual',
  }
}

function mapWeatherAlert(alert) {
  return {
    externalId: alert.external_id,
    sourceName: alert.source_name,
    title: alert.title,
    summary: alert.summary ?? '',
    severity: alert.severity ?? 'informativo',
    status: alert.status ?? 'ativo',
    area: alert.area ?? '',
    areas: alert.areas ?? [],
    sourceUrl: alert.source_url ?? null,
    publishedAt: formatPublishedAt(alert.published_at),
    effectiveAt: formatPublishedAt(alert.effective_at),
    expiresAt: formatPublishedAt(alert.expires_at),
    isActive: Boolean(alert.is_active),
  }
}

function mapWeatherOverview(payload) {
  return {
    summary: {
      headline: payload.summary.headline,
      description: payload.summary.summary,
      advisoryItems: payload.summary.advisory_items ?? [],
      sourceNames: payload.summary.source_names ?? [],
      updatedAt: formatPublishedAt(payload.summary.updated_at),
      locationCount: payload.summary.location_count ?? 0,
      activeAlertCount: payload.summary.active_alert_count ?? 0,
      severeAlertCount: payload.summary.severe_alert_count ?? 0,
    },
    locations: (payload.locations ?? []).map(mapWeatherLocation),
    alerts: (payload.alerts ?? []).map(mapWeatherAlert),
  }
}

export async function fetchHomeData() {
  const payload = await request('/home')
  return mapHome(payload)
}

export async function fetchCategoryPage(page) {
  const payload = await request(`/categories/${page}`)
  return mapCategoryDetail(payload)
}

export async function fetchArticlePage(slug) {
  const payload = await request(`/articles/slug/${slug}`)
  return mapArticleDetail(payload)
}

export async function fetchPublishedArticles({ limit = 100, offset = 0 } = {}) {
  const normalizedLimit = Math.max(1, Number(limit) || 1)
  const normalizedOffset = Math.max(0, Number(offset) || 0)
  const pageSize = 50
  const items = []
  let currentOffset = normalizedOffset
  let hasMore = false

  while (items.length < normalizedLimit) {
    const batchLimit = Math.min(pageSize, normalizedLimit - items.length)
    const params = new URLSearchParams({
      limit: String(batchLimit),
      offset: String(currentOffset),
    })
    const payload = await request(`/articles/published?${params.toString()}`)
    const batchItems = (payload.items ?? []).map(mapArticleCard)

    items.push(...batchItems)
    hasMore = payload.has_more ?? false

    if (!hasMore || batchItems.length === 0) {
      break
    }

    currentOffset += batchItems.length
  }

  return {
    items,
    hasMore,
  }
}

export async function searchPublishedArticles(query, { limit = 6 } = {}) {
  const normalizedQuery = String(query ?? '').trim()
  if (normalizedQuery.length < 2) {
    return {
      items: [],
      hasMore: false,
    }
  }

  const params = new URLSearchParams({
    q: normalizedQuery,
    limit: String(Math.max(1, Number(limit) || 1)),
  })
  const payload = await request(`/articles/search?${params.toString()}`)

  return {
    items: (payload.items ?? []).map(mapArticleCard),
    hasMore: payload.has_more ?? false,
  }
}

export async function fetchVideosPage() {
  const { items } = await fetchPublishedArticles({ limit: 150 })
  const videoArticles = items.filter((article) => article.videoUrl)
  const featuredArticle = videoArticles[0] ?? null

  return {
    page: 'videos',
    eyebrow: 'Videos',
    title: 'Videos',
    description:
      'Materias publicadas que chegaram com link de video entram nesta pagina para concentrar entrevistas, cortes e cobertura em formato visual.',
    railTitle: 'O que aparece aqui',
    railItems: [
      'Materias publicadas com video_url disponivel no backend',
      'Entradas visuais vindas de diferentes editorias do portal',
      'Leitura por materia com continuidade para a reportagem completa',
    ],
    featuredArticle,
    articles: videoArticles,
    hasMore: false,
  }
}

export async function fetchWeatherOverview() {
  const payload = await request('/weather/overview')
  return mapWeatherOverview(payload)
}

export { ApiError }
