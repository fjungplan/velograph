import { useState } from 'react';
import { useTimeline } from '../hooks/useTeamData';
import { useResponsive } from '../hooks/useResponsive';
import { LoadingSpinner } from '../components/Loading';
import { ErrorDisplay } from '../components/ErrorDisplay';
import TimelineGraph from '../components/TimelineGraph';
import './HomePage.css';

function HomePage() {
  const { isMobile } = useResponsive();
  const currentYear = new Date().getFullYear();
  
  const [filters, setFilters] = useState({
    start_year: 2020,
    end_year: currentYear,
    tier_filter: [1, 2, 3]
  });
  
  const { data, isLoading, error, refetch } = useTimeline(filters);
  
  const handleYearRangeChange = (startYear, endYear) => {
    setFilters(prev => ({
      ...prev,
      start_year: startYear,
      end_year: endYear
    }));
  };
  
  const handleTierFilterChange = (tiers) => {
    setFilters(prev => ({
      ...prev,
      tier_filter: tiers.length > 0 ? tiers : null
    }));
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading timeline..." size="lg" />;
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={refetch} />;
  }

  return isMobile ? (
    <div className="home-page">
      <h2>Mobile View</h2>
      <p>Mobile list view coming soon...</p>
      <div className="data-summary">
        <div className="summary-card">
          <h3>Nodes</h3>
          <p className="summary-value">{data?.nodes?.length || 0}</p>
        </div>
        <div className="summary-card">
          <h3>Links</h3>
          <p className="summary-value">{data?.links?.length || 0}</p>
        </div>
      </div>
    </div>
  ) : (
    <TimelineGraph 
      data={data} 
      onYearRangeChange={handleYearRangeChange}
      onTierFilterChange={handleTierFilterChange}
      initialStartYear={filters.start_year}
      initialEndYear={filters.end_year}
      initialTiers={filters.tier_filter || [1, 2, 3]}
      onEditSuccess={refetch}
    />
  );
}

export default HomePage;
