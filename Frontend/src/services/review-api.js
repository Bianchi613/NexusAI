import { request } from './api-client'

function buildQuery(params) {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return
    }
    searchParams.set(key, String(value))
  })

  const queryString = searchParams.toString()
  return queryString ? `?${queryString}` : ''
}

export function listPendingReviewArticles(reviewerId, { limit = 20, offset = 0 } = {}) {
  return request(
    `/review/articles/pending${buildQuery({
      reviewer_id: reviewerId,
      limit,
      offset,
    })}`,
  )
}

export function listReviewArticles(
  reviewerId,
  { limit = 30, offset = 0, status, categoryId, reviewedBy } = {},
) {
  return request(
    `/review/articles${buildQuery({
      reviewer_id: reviewerId,
      limit,
      offset,
      status,
      category_id: categoryId,
      reviewed_by: reviewedBy,
    })}`,
  )
}

export function getReviewArticle(reviewerId, articleId) {
  return request(`/review/articles/${articleId}${buildQuery({ reviewer_id: reviewerId })}`)
}

export function createReviewArticle(reviewerId, payload) {
  return request(`/review/articles${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateReviewArticle(reviewerId, articleId, payload) {
  return request(`/review/articles/${articleId}${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteReviewArticle(reviewerId, articleId) {
  return request(`/review/articles/${articleId}${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'DELETE',
  })
}

export function approveReviewArticle(reviewerId, articleId) {
  return request(`/review/articles/${articleId}/approve`, {
    method: 'PATCH',
    body: JSON.stringify({ reviewer_id: reviewerId }),
  })
}

export function rejectReviewArticle(reviewerId, articleId) {
  return request(`/review/articles/${articleId}/reject`, {
    method: 'PATCH',
    body: JSON.stringify({ reviewer_id: reviewerId }),
  })
}

export function listReviewCategories(reviewerId, { limit = 100, offset = 0 } = {}) {
  return request(
    `/review/categories${buildQuery({
      reviewer_id: reviewerId,
      limit,
      offset,
    })}`,
  )
}

export function createReviewCategory(reviewerId, payload) {
  return request(`/review/categories${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateReviewCategory(reviewerId, categoryId, payload) {
  return request(`/review/categories/${categoryId}${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteReviewCategory(reviewerId, categoryId) {
  return request(`/review/categories/${categoryId}${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'DELETE',
  })
}

export function listReviewTags(reviewerId, { limit = 100, offset = 0 } = {}) {
  return request(
    `/review/tags${buildQuery({
      reviewer_id: reviewerId,
      limit,
      offset,
    })}`,
  )
}

export function createReviewTag(reviewerId, payload) {
  return request(`/review/tags${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateReviewTag(reviewerId, tagId, payload) {
  return request(`/review/tags/${tagId}${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteReviewTag(reviewerId, tagId) {
  return request(`/review/tags/${tagId}${buildQuery({ reviewer_id: reviewerId })}`, {
    method: 'DELETE',
  })
}
