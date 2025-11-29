import './Loading.css';

export function LoadingSpinner({ size = 'md', message }) {
  const sizeClass = `spinner-${size}`;
  
  return (
    <div className="loading-container">
      <div className={`spinner ${sizeClass}`}>
        <div className="spinner-circle"></div>
      </div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  );
}

export function LoadingSkeleton({ type = 'card' }) {
  const skeletonClass = `skeleton-${type}`;
  
  return (
    <div className={`skeleton-container ${skeletonClass}`}>
      {type === 'list' && (
        <>
          <div className="skeleton-item">
            <div className="skeleton-line skeleton-line-full"></div>
            <div className="skeleton-line skeleton-line-medium"></div>
          </div>
          <div className="skeleton-item">
            <div className="skeleton-line skeleton-line-full"></div>
            <div className="skeleton-line skeleton-line-medium"></div>
          </div>
          <div className="skeleton-item">
            <div className="skeleton-line skeleton-line-full"></div>
            <div className="skeleton-line skeleton-line-medium"></div>
          </div>
        </>
      )}
      
      {type === 'graph' && (
        <div className="skeleton-graph">
          <div className="skeleton-graph-header skeleton-pulse"></div>
          <div className="skeleton-graph-body skeleton-pulse"></div>
        </div>
      )}
      
      {type === 'card' && (
        <div className="skeleton-card">
          <div className="skeleton-line skeleton-line-full skeleton-pulse"></div>
          <div className="skeleton-line skeleton-line-medium skeleton-pulse"></div>
          <div className="skeleton-line skeleton-line-short skeleton-pulse"></div>
        </div>
      )}
    </div>
  );
}
