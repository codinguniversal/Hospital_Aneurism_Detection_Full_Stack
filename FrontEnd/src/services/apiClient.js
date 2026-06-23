import { API_BASE_URL } from './config.js'

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`)
  }

  return response.json()
}

export const emailApi = {
  async checkEmailExists(email) {
    return apiRequest(`/email/check?email=${encodeURIComponent(email)}`)
      .then(data => data.exists)
  }
}
