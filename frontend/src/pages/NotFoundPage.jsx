import { Link } from 'react-router-dom';
import './NotFoundPage.css';

function NotFoundPage() {
  return (
    <div className="not-found-page">
      <h1 className="error-code">404</h1>
      <h2>Page Not Found</h2>
      <p>The page you're looking for doesn't exist or has been moved.</p>
      <Link to="/" className="home-link">
        Go to Home
      </Link>
    </div>
  );
}

export default NotFoundPage;
