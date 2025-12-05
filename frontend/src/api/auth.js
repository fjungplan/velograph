import apiClient from './client';

export const authApi = {
  googleAuth: (idToken) => 
    apiClient.post('/api/v1/auth/google', { id_token: idToken }),
  
  refreshToken: (refreshToken) =>
    apiClient.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
  
  getCurrentUser: (token) =>
    apiClient.get('/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    }),
};
