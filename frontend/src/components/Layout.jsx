import { Outlet, Link } from 'react-router-dom';
import './Layout.css';

function Layout() {
  return (
    <div className="layout">
      <header className="layout-header">
        <div className="layout-header-content">
          <h1 className="layout-title">Cycling Team Lineage</h1>
          <nav className="layout-nav">
            <Link to="/" className="nav-link">Home</Link>
          </nav>
        </div>
      </header>

      <main className="layout-main">
        <Outlet />
      </main>

      <footer className="layout-footer">
        <p>&copy; {new Date().getFullYear()} Cycling Team Lineage. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default Layout;
