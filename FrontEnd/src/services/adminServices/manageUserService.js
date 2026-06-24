import apiClient from '../apiClient';
import axios from 'axios'
//for admin user management page//

export const userService = {
  /**
   * Fetches all registered staff accounts from the backend database.
   */
  async getAllUsers() {
    return apiClient.get('/users');
  },

  /**
   * Registers a brand-new medical staff profile record in MongoDB.
   */
    async register(email, password) {
        // 1. Grab the token you just received during login (adjust localStorage key if named differently)
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

        // 2. Send the exact payload body AND the Authorization header
        return await axios.post('http://localhost:8000/auth/register', 
        {
            email: email,
            password: password,
        },
        {
            headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
            }
        }
        );
  },

  /**
   * Validates if an email address is already locked to an active profile.
   */
  async checkEmailExists(email) {
    const response = await apiClient.get('/auth/check-email', {
      params: { email } 
    });
    const data = response.data || response;
    return data.exists;
  },

  /**
   * Deletes a staff record by its unique employee identity.
   */
  async deleteUser(userId) {
    return apiClient.delete(`/users/${userId}`);
  }
};