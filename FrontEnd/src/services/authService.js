import { API_BASE_URL , apiRequest } from './config.js'



export const authApi = {
  async register(email, password, gender) {
    return apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, gender })
    })
  },

  async login(loginIdentifier, password, isAdmin) {
    const responseData = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ loginIdentifier, password, isAdmin })
    })

    return {
      status: responseData.status,
      employeeId: responseData.user_id // Maps "user_id"  to "employeeId"
    }
  }
}


export const emailApi = {
  async checkEmailExists(email) {
    return apiRequest(`/email/check?email=${encodeURIComponent(email)}`)
      .then(data => data.exists)
  }
}
