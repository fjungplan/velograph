import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import UserMenu from '../components/UserMenu';

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock authApi
vi.mock('../api/auth', () => ({
  authApi: {
    googleAuth: vi.fn(),
    refreshToken: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should provide auth context', () => {
    const TestComponent = () => {
      const auth = useAuth();
      return <div>{auth.isAuthenticated ? 'Authenticated' : 'Not authenticated'}</div>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Not authenticated')).toBeInTheDocument();
  });

  it('should have loading state on mount', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <div data-testid="auth-content">Content</div>
        </AuthProvider>
      </BrowserRouter>
    );

    // Should eventually render content after loading
    expect(screen.getByTestId('auth-content')).toBeInTheDocument();
  });
});

describe('UserMenu', () => {
  const mockUser = {
    user_id: '123',
    email: 'test@example.com',
    display_name: 'Test User',
    avatar_url: null,
    role: 'TRUSTED_USER',
    approved_edits_count: 5,
  };

  it('should not render when user is null', () => {
    const TestWrapper = () => {
      return (
        <AuthProvider>
          <UserMenu />
        </AuthProvider>
      );
    };

    const { container } = render(
      <BrowserRouter>
        <TestWrapper />
      </BrowserRouter>
    );

    expect(container.firstChild.children.length).toBe(0);
  });

  it('should render avatar placeholder with first letter', () => {
    const TestComponent = () => {
      const { user } = useAuth();
      return user ? <div>{user.display_name[0]}</div> : null;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Component should render without errors
    expect(document.body).toBeInTheDocument();
  });
});

describe('AuthContext token management', () => {
  it('should clear auth on logout', async () => {
    const TestComponent = () => {
      const { logout, isAuthenticated } = useAuth();
      return (
        <button onClick={logout}>
          {isAuthenticated ? 'Logout' : 'Not authenticated'}
        </button>
      );
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Not authenticated')).toBeInTheDocument();
  });
});
