
// Use the VITE_API_URL for development, but a relative path for production.
export const apiUrl = import.meta.env.PROD ? '/api' : import.meta.env.VITE_API_URL + '/api';