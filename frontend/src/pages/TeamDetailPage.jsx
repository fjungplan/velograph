import { useParams } from 'react-router-dom';
import { useTeamHistory } from '../hooks/useTeamData';
import { LoadingSpinner } from '../components/Loading';
import { ErrorDisplay } from '../components/ErrorDisplay';
import './TeamDetailPage.css';

function TeamDetailPage() {
  const { nodeId } = useParams();
  const { data, isLoading, error, refetch } = useTeamHistory(nodeId);

  if (isLoading) {
    return <LoadingSpinner message="Loading team history..." size="lg" />;
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={refetch} />;
  }

  return (
    <div className="team-detail-page">
      <h2>Team History</h2>
      
      <div className="team-overview">
        <p><strong>Node ID:</strong> {data?.node_id}</p>
        <p><strong>Founded:</strong> {data?.founding_year}</p>
        {data?.dissolution_year && (
          <p><strong>Dissolved:</strong> {data?.dissolution_year}</p>
        )}
      </div>

      <h3>Timeline</h3>
      {data?.timeline && data.timeline.length > 0 ? (
        <div className="timeline-list">
          {data.timeline.map((era, index) => (
            <div key={index} className="timeline-era">
              <div className="era-year">{era.year}</div>
              <div className="era-details">
                <h4>{era.name}</h4>
                {era.tier && <p className="era-tier">Tier {era.tier}</p>}
                {era.uci_code && <p className="era-uci">UCI Code: {era.uci_code}</p>}
                <p className="era-status">{era.status}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p>No timeline data available.</p>
      )}

      <details className="data-preview">
        <summary>View Raw Data</summary>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </details>
    </div>
  );
}

export default TeamDetailPage;
