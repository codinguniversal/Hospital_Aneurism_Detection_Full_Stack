import apiClient from './apiClient'; 

export const authService = {

async login(loginIdentifier, password, isAdmin) {
    // Send standard JSON body matching LoginRequestSchema keys perfectly
    const response = await apiClient.post('/auth/login', {
      loginIdentifier,
      password,
      isAdmin
    });

  console.log(`Login response received: ${JSON.stringify(response)}`); // Debugging log
  const responseData = response.data || response; // Axios response interceptor already returns raw data    

    if (responseData.access_token) {
      localStorage.setItem('access_token', responseData.access_token);
      localStorage.setItem('user_role', responseData.role);
      localStorage.setItem('employee_id', responseData.employee_id);
    }

    return {
      employeeId: responseData.employee_id,
      email: responseData.email,
      role: responseData.role
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
