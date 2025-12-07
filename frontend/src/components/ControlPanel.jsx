import { useEffect, useState } from 'react';
import SearchBar from './SearchBar';
import './ControlPanel.css';

export default function ControlPanel({ 
  onYearRangeChange, 
  onTierFilterChange,
  onZoomReset,
  onTeamSelect,
  searchNodes = [],
  initialStartYear = 2020,
  initialEndYear = new Date().getFullYear(),
  initialTiers = [1, 2, 3]
}) {
  const currentYear = new Date().getFullYear();
  const [startYear, setStartYear] = useState(initialStartYear);
  const [endYear, setEndYear] = useState(initialEndYear);
  const [selectedTiers, setSelectedTiers] = useState(initialTiers);

  // Keep local state in sync when parent updates
  useEffect(() => {
    setStartYear(initialStartYear);
    setEndYear(initialEndYear);
    setSelectedTiers(initialTiers);
  }, [initialStartYear, initialEndYear, initialTiers]);
  
  const handleApply = () => {
    onYearRangeChange(startYear, endYear);
    onTierFilterChange(selectedTiers);
  };
  
  const handleReset = () => {
    // Reset to default values
    setStartYear(1900);
    setEndYear(currentYear);
    setSelectedTiers([1, 2, 3]);
    // Apply reset filters
    onYearRangeChange(1900, currentYear);
    onTierFilterChange([1, 2, 3]);
    // Clear team selection and reset zoom
    onTeamSelect?.(null);
    onZoomReset();
  };
  
  const toggleTier = (tier) => {
    setSelectedTiers(prev => 
      prev.includes(tier) 
        ? prev.filter(t => t !== tier)
        : [...prev, tier].sort()
    );
  };
  
  return (
    <div className="control-panel">
      {searchNodes.length > 0 && (
        <div className="control-section">
          <h3>Find Team</h3>
          <SearchBar 
            nodes={searchNodes}
            onTeamSelect={onTeamSelect}
          />
        </div>
      )}

      <div className="control-section">
        <h3>Year Range</h3>
        <div className="year-inputs">
          <label>
            Start:
            <input 
              type="number" 
              value={startYear} 
              onChange={(e) => setStartYear(parseInt(e.target.value))}
              min={1900}
              max={endYear}
            />
          </label>
          <label>
            End:
            <input 
              type="number" 
              value={endYear} 
              onChange={(e) => setEndYear(parseInt(e.target.value))}
              min={startYear}
              max={currentYear}
            />
          </label>
        </div>
      </div>
      
      <div className="control-section">
        <h3>Tier Filters</h3>
        <div className="tier-checkboxes">
          {[1, 2, 3].map(tier => (
            <label key={tier}>
              <input 
                type="checkbox" 
                checked={selectedTiers.includes(tier)}
                onChange={() => toggleTier(tier)}
              />
              {tier === 1 ? 'WorldTour' : tier === 2 ? 'ProTeam' : 'Continental'}
            </label>
          ))}
        </div>
      </div>
      
      <div className="control-actions">
        <button onClick={handleApply}>Apply Filters</button>
        <button onClick={handleReset}>Reset Filters</button>
      </div>
    </div>
  );
}
