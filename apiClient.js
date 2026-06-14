import axios from 'axios';

/**
 * Configurable API client for backend communication.
 * 
 * Base URL can be configured via:
 * 1. VITE_API_URL environment variable (preferred for deployments)
 * 2. Defaults to same-origin /api requests through the Vite dev proxy
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for graph analysis
});

/**
 * Add response interceptor for better error handling
 */
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Enhanced error message extraction
    if (error.response?.data?.detail) {
      error.message = error.response.data.detail;
    } else if (error.message === 'Network Error' && !error.response) {
      const apiLocation = API_BASE_URL || 'the configured /api proxy';
      error.message = `Cannot connect to API server at ${apiLocation}. Is the backend running?`;
    }
    return Promise.reject(error);
  }
);

export default apiClient;
