import { useParams } from 'react-router-dom';
import './TeamDetailPage.css';

function TeamDetailPage() {
  const { nodeId } = useParams();

  return (
    <div className="team-detail-page">
      <h2>Team Detail for {nodeId}</h2>
      <p>Detailed team information will be displayed here.</p>
      <div className="placeholder-content">
        <p>This page will show:</p>
        <ul>
          <li>Team history and lineage</li>
          <li>Key transitions and events</li>
          <li>Related teams and sponsors</li>
        </ul>
      </div>
    </div>
  );
}

export default TeamDetailPage;
