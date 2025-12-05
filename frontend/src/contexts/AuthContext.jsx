import { createContext, useContext, useState, useEffect } from 'react';
import { googleLogout } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { authApi } from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);

  useEffect(() => {
    // Load tokens from localStorage on mount
    const storedAccessToken = localStorage.getItem('accessToken');
    const storedRefreshToken = localStorage.getItem('refreshToken');

    if (storedAccessToken && storedRefreshToken) {
      // Verify token is not expired
      try {
        const decoded = jwtDecode(storedAccessToken);
        if (decoded.exp * 1000 > Date.now()) {
          setAccessToken(storedAccessToken);
          setRefreshToken(storedRefreshToken);
          loadUserInfo(storedAccessToken);
        } else {
          // Try to refresh
          refreshAccessToken(storedRefreshToken);
        }
      } catch (error) {
        console.error('Invalid token:', error);
        clearAuth();
      }
    } else {
      setLoading(false);
    }
  }, []);

  const loadUserInfo = async (token) => {
    try {
      const response = await authApi.getCurrentUser(token);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to load user info:', error);
      clearAuth();
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const response = await authApi.googleAuth(credentialResponse.credential);
      const { access_token, refresh_token } = response.data;

      // Store tokens
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);

      setAccessToken(access_token);
      setRefreshToken(refresh_token);

      // Load user info
      await loadUserInfo(access_token);
    } catch (error) {
      console.error('Google auth failed:', error);
      throw error;
    }
  };

  const refreshAccessToken = async (refToken) => {
    try {
      const response = await authApi.refreshToken(refToken);
      const { access_token, refresh_token } = response.data;

      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);

      setAccessToken(access_token);
      setRefreshToken(refresh_token);

      await loadUserInfo(access_token);

      return access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      clearAuth();
      throw error;
    }
  };

  const logout = () => {
    googleLogout();
    clearAuth();
  };

  const clearAuth = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    setLoading(false);
  };

  const isAdmin = () => {
    return user?.role === 'ADMIN';
  };

  const canEdit = () => {
    return user && ['NEW_USER', 'TRUSTED_USER', 'ADMIN'].includes(user.role);
  };

  const needsModeration = () => {
    return user?.role === 'NEW_USER';
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      accessToken,
      refreshToken,
      handleGoogleSuccess,
      refreshAccessToken,
      logout,
      isAuthenticated: !!user,
      isAdmin,
      canEdit,
      needsModeration
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
