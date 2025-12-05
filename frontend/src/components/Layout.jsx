import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import UserMenu from './UserMenu';
import './Layout.css';

function Layout() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="layout">
        <div className="loading-screen">Loading...</div>
      </div>
    );
  }

  return (
    <div className="layout">
      <header className="layout-header">
        <div className="layout-header-content">
          <Link to="/" className="layout-title-link">
            <h1 className="layout-title">ChainLines</h1>
          </Link>
          <nav className="layout-nav">
            {isAuthenticated ? (
              <UserMenu />
            ) : (
              <Link to="/login" className="nav-link login-link">
                Sign In
              </Link>
            )}
          </nav>
        </div>
      </header>

      <main className="layout-main">
        <Outlet />
      </main>

      <footer className="layout-footer">
        <p>&copy; {new Date().getFullYear()} ChainLines. Open Source Project.</p>
      </footer>
    </div>
  );
}

export default Layout;
