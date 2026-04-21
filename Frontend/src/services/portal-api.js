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
    body: payload.body_paragraphs ?? [],
    tags: (payload.tags ?? []).map((tag) => tag.name),
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

export { ApiError }
