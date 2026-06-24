import apiClient from '../apiClient';

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
  async register(employeeId, email, password) {
    // 🎯 Matches your AdminView.vue call signatures perfectly
    return apiClient.post('/auth/register', { 
      employee_id: employeeId, 
      email, 
      password 
    });
  },

  /**
   * Validates if an email address is already locked to an active profile.
   */
  async checkEmailExists(email) {
    const response = await apiClient.get('/email/check', {
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