import { API_BASE_URL , apiRequest } from './config.js'



export const authApi = {
  async register(username, email, password, gender) {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, gender })
    })
  },

  async login(loginIdentifier, password, isAdmin) {
    return apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ loginIdentifier, password, isAdmin })
    })
  }
}


export const emailApi = {
  async checkEmailExists(email) {
    return apiRequest(`/email/check?email=${encodeURIComponent(email)}`)
      .then(data => data.exists)
  }
}
