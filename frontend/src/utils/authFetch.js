/**
 * Authenticated fetch wrapper
 * Automatically adds Authorization header with JWT token
 */
export const authFetch = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');

  const headers = {
    ...options.headers,
  };

  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  return fetch(url, config);
};
