import axios from 'axios';

// Establish the clean backend root context
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. Request Interceptor: Automatically bake your JWT token into outgoing packets
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. Response Interceptor: Seamlessly manage global security gatekeeper logic
apiClient.interceptors.response.use(
  (response) => response.data, // Strip away axios metabolic wrappers so views receive raw JSON data directly
  (error) => {
    if (error.response) {
      const status = error.response.status;

      // Handle token expiration or unauthorized exceptions uniformly
      if (status === 401) {
        console.warn('Session expired or unauthorized. Clearing state...');
        localStorage.removeItem('access_token');
        // If using Vue Router or native windows, redirect here:
        window.location.href = '/login'; 
      }
      
      if (status === 403) {
        alert("Security Alert: You do not have the required role permissions to view this resource.");
      }
    }
    // Keep the Axios error intact so callers can read the HTTP status and
    // backend detail instead of receiving an unhelpful generic message.
    return Promise.reject(error);
  }
);

export default apiClient;
