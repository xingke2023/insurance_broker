import axios from 'axios';
import { API_BASE_URL } from '../config';

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// Setup axios interceptor for handling 401 errors
export const setupAxiosInterceptors = (onLogout) => {
  // Request interceptor to add token to every request
  axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor to handle 401 errors
  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    async (error) => {
      const originalRequest = error.config;

      // If error is 401 and we haven't tried to refresh yet
      if (error.response?.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          // If already refreshing, queue this request
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then(token => {
              originalRequest.headers['Authorization'] = `Bearer ${token}`;
              return axios(originalRequest);
            })
            .catch(err => {
              return Promise.reject(err);
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          // No refresh token, logout
          console.error('No refresh token found, logging out');
          isRefreshing = false;
          if (onLogout) onLogout();
          return Promise.reject(error);
        }

        try {
          // Try to refresh the token
          const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
            refresh: refreshToken
          });

          const { access } = response.data;

          // Save new token
          localStorage.setItem('access_token', access);
          axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;

          // Process queued requests
          processQueue(null, access);
          isRefreshing = false;

          // Retry original request with new token
          originalRequest.headers['Authorization'] = `Bearer ${access}`;
          return axios(originalRequest);
        } catch (refreshError) {
          // Refresh failed, logout
          console.error('Token refresh failed, logging out', refreshError);
          processQueue(refreshError, null);
          isRefreshing = false;

          // Clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');

          if (onLogout) onLogout();

          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );
};
