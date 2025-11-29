import { useTimeline } from '../hooks/useTeamData';
import { LoadingSpinner } from '../components/Loading';
import { ErrorDisplay } from '../components/ErrorDisplay';
import './HomePage.css';

function HomePage() {
  const { data, isLoading, error, refetch } = useTimeline({
    start_year: 2020,
    end_year: 2024,
  });

  if (isLoading) {
    return <LoadingSpinner message="Loading timeline..." size="lg" />;
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={refetch} />;
  }

  return (
    <div className="home-page">
      <h2>Timeline Data Loaded</h2>
      <p>Successfully loaded timeline data from the backend API.</p>
      
      <div className="data-summary">
        <div className="summary-card">
          <h3>Nodes</h3>
          <p className="summary-value">{data?.nodes?.length || 0}</p>
        </div>
        <div className="summary-card">
          <h3>Links</h3>
          <p className="summary-value">{data?.links?.length || 0}</p>
        </div>
        <div className="summary-card">
          <h3>Year Range</h3>
          <p className="summary-value">
            {data?.meta?.year_range?.[0]} - {data?.meta?.year_range?.[1]}
          </p>
        </div>
      </div>

      <details className="data-preview">
        <summary>View Raw Data</summary>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </details>
    </div>
  );
}

export default HomePage;
