export const API_ROOT = (import.meta.env.VITE_API_BASE_URL ?? '/api/v1').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

function getApiErrorMessage(payload) {
  const detail = payload?.detail

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => {
        if (typeof item === 'string') {
          return item
        }

        if (typeof item?.msg === 'string') {
          return item.msg
        }

        return null
      })
      .filter(Boolean)
      .join(' | ')
  }

  if (typeof payload?.message === 'string' && payload.message.trim()) {
    return payload.message
  }

  return 'Nao foi possivel carregar os dados do portal.'
}

export async function request(path, options = {}) {
  const response = await fetch(`${API_ROOT}${path}`, {
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers ?? {}),
    },
    ...options,
  })

  const isJson = response.headers.get('content-type')?.includes('application/json')
  const payload = isJson ? await response.json() : null

  if (!response.ok) {
    throw new ApiError(getApiErrorMessage(payload), response.status, payload)
  }

  return payload
}
