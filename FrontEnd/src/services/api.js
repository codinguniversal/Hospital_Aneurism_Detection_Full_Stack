// API service backend 
const API_BASE_URL = 'http://localhost:8000'  // Update this to your backend URL

export const emailApi = {
  // Check if email already exists
  async checkEmailExists(email) {
    try {
      const response = await fetch(`${API_BASE_URL}/email/check?email=${encodeURIComponent(email)}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      return data.exists
    } catch (error) {
      console.error('Email check error:', error)
      throw error
    }
  }
}

export const authApi = {
  // Register new user
  async register(username, email, password, gender) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username,
          email,
          password,
          gender
        })
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Register error:', error)
      throw error
    }
  },

  // Login
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }
}
