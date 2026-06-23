import apiClient from './apiClient'; 

export const authService = {

  async register(email, password, gender) {
    // Axios automatically handles JSON stringification and content headers
    return apiClient.post('/auth/register', { 
      email, 
      password, 
      gender 
    });
  },

  async login(loginIdentifier, password, isAdmin) {
    const data = await apiClient.post('/auth/login', {
      loginIdentifier,
      password,
      isAdmin
    });

    //  Capture and store the JWT and user properties returned by your successful backend response
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_role', data.role);
      localStorage.setItem('employee_id', data.employee_id);
    }

    // Return the clean entity mapping to your frontend views
    return {
      employeeId: data.employee_id,
      email: data.email,
      role: data.role
    };
  },

  /**
   * Destroys session signatures to cleanly terminate application state.
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('employee_id');
    window.location.href = '/login';
  }
};

export const emailService = {
  async checkEmailExists(email) {
    const data = await apiClient.get('/email/check', {
      params: { email } 
    });
    return data.exists;
  }
};