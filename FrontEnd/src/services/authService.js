import apiClient from './apiClient'; 

export const authService = {

async login(loginIdentifier, password) {
  // Cleaned: Removed 'isAdmin' parameter from the JSON body payload
  const response = await apiClient.post('/auth/login', {
    loginIdentifier,
    password
  });

  console.log(`Login response received: ${JSON.stringify(response)}`);
  const responseData = response.data || response;   

  if (responseData.access_token) {
    localStorage.setItem('access_token', responseData.access_token);
    localStorage.setItem('user_role', responseData.role); // Extracted safely from DB
    localStorage.setItem('employee_id', responseData.employee_id);
  }

  return {
    employeeId: responseData.employee_id,
    email: responseData.email,
    role: responseData.role
  };
},

logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_role');
  localStorage.removeItem('employee_id');
  window.location.href = '/login';
}
}