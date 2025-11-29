import './HomePage.css';

function HomePage() {
  return (
    <div className="home-page">
      <h2>Home - Visualization coming soon</h2>
      <p>
        Welcome to the Cycling Team Lineage application. The interactive timeline
        visualization will be displayed here.
      </p>
      <div className="api-info">
        <p>Backend API: <code>{import.meta.env.VITE_API_URL || 'http://localhost:8000'}</code></p>
      </div>
    </div>
  );
}

export default HomePage;
