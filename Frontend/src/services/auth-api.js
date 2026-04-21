import { ApiError, request } from './api-client'

const ACCESS_TOKEN_KEY = 'nexus_ai_access_token'

function isBrowser() {
  return typeof window !== 'undefined'
}

export function getStoredAccessToken() {
  if (!isBrowser()) {
    return null
  }
  return window.localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function storeAccessToken(token) {
  if (!isBrowser()) {
    return
  }
  window.localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function clearAccessToken() {
  if (!isBrowser()) {
    return
  }
  window.localStorage.removeItem(ACCESS_TOKEN_KEY)
}

export async function loginWithPassword({ email, password }) {
  const payload = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })

  if (payload?.access_token) {
    storeAccessToken(payload.access_token)
  }

  return payload
}

export async function registerWithPassword({ name, email, password }) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  })
}

export async function fetchCurrentUser() {
  const token = getStoredAccessToken()
  if (!token) {
    return null
  }

  try {
    return await request('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      clearAccessToken()
      return null
    }
    throw error
  }
}

export async function registerAndLogin({ name, email, password }) {
  await registerWithPassword({ name, email, password })
  await loginWithPassword({ email, password })
  return fetchCurrentUser()
}
