import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { editsApi } from '../api/edits';
import { teamsApi } from '../api/teams';
import './MergeWizard.css';

export default function MergeWizard({ initialNode, onClose, onSuccess }) {
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    source_nodes: initialNode ? [initialNode] : [],
    merge_year: new Date().getFullYear(),
    new_team_name: '',
    new_team_tier: '',
    reason: ''
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    if (searchTerm.length >= 2) {
      searchTeams();
    } else {
      setSearchResults([]);
    }
  }, [searchTerm]);
  
  const searchTeams = async () => {
    try {
      const response = await teamsApi.getTeams({ search: searchTerm });
      // Filter out already selected teams
      const selectedIds = formData.source_nodes.map(n => n.id);
      const filtered = response.data.items.filter(
        team => !selectedIds.includes(team.id)
      );
      setSearchResults(filtered);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };
  
  const addSourceTeam = (team) => {
    if (formData.source_nodes.length >= 5) {
      setError('Maximum 5 teams can be merged');
      return;
    }
    
    setFormData(prev => ({
      ...prev,
      source_nodes: [...prev.source_nodes, team]
    }));
    setSearchTerm('');
    setSearchResults([]);
  };
  
  const removeSourceTeam = (teamId) => {
    setFormData(prev => ({
      ...prev,
      source_nodes: prev.source_nodes.filter(t => t.id !== teamId)
    }));
  };
  
  const handleNext = () => {
    if (step === 1 && formData.source_nodes.length < 2) {
      setError('Select at least 2 teams to merge');
      return;
    }
    setError(null);
    setStep(step + 1);
  };
  
  const handleBack = () => {
    setError(null);
    setStep(step - 1);
  };
  
  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    
    try {
      const response = await editsApi.createMerge({
        source_node_ids: formData.source_nodes.map(n => n.id),
        merge_year: parseInt(formData.merge_year),
        new_team_name: formData.new_team_name,
        new_team_tier: parseInt(formData.new_team_tier),
        reason: formData.reason
      });
      
      onSuccess(response.data);
    } catch (err) {
      const errorDetail = err.response?.data?.detail;
      if (Array.isArray(errorDetail)) {
        // Pydantic validation errors
        setError(errorDetail.map(e => e.msg).join(', '));
      } else if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else {
        setError('Failed to create merge. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <div className="wizard-overlay" onClick={onClose}>
      <div className="wizard-modal large" onClick={(e) => e.stopPropagation()}>
        <div className="wizard-header">
          <h2>Create Team Merger</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="wizard-progress">
          <div className={`step ${step >= 1 ? 'active' : ''}`}>1. Select Teams</div>
          <div className={`step ${step >= 2 ? 'active' : ''}`}>2. Merge Details</div>
          <div className={`step ${step >= 3 ? 'active' : ''}`}>3. Review</div>
        </div>
        
        <div className="wizard-content">
          {step === 1 && (
            <div className="step-content">
              <h3>Select Teams to Merge</h3>
              
              <div className="selected-teams">
                <h4>Selected Teams ({formData.source_nodes.length}/5)</h4>
                {formData.source_nodes.map(team => {
                  const latestEra = team.eras?.[team.eras.length - 1];
                  return (
                    <div key={team.id} className="selected-team">
                      <span>{latestEra?.name || 'Unknown Team'}</span>
                      <button onClick={() => removeSourceTeam(team.id)}>Remove</button>
                    </div>
                  );
                })}
              </div>
              
              <div className="team-search">
                <input
                  type="text"
                  placeholder="Search for teams..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                {searchResults.length > 0 && (
                  <div className="search-results">
                    {searchResults.map(team => (
                      <div 
                        key={team.id}
                        className="search-result"
                        onClick={() => addSourceTeam(team)}
                      >
                        <span>{team.eras[team.eras.length - 1].name}</span>
                        <span className="years">
                          {team.founding_year} - {team.dissolution_year || 'present'}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
          
          {step === 2 && (
            <div className="step-content">
              <h3>Merge Details</h3>
              
              <label>
                Merge Year
                <input
                  type="number"
                  value={formData.merge_year}
                  onChange={(e) => setFormData(prev => ({ ...prev, merge_year: e.target.value }))}
                  min={1900}
                  max={new Date().getFullYear() + 1}
                  required
                />
              </label>
              
              <label>
                New Team Name
                <input
                  type="text"
                  value={formData.new_team_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, new_team_name: e.target.value }))}
                  placeholder="e.g., Team Visma | Lease a Bike"
                  required
                />
              </label>
              
              <label>
                New Team Tier
                <select
                  value={formData.new_team_tier}
                  onChange={(e) => setFormData(prev => ({ ...prev, new_team_tier: e.target.value }))}
                  required
                >
                  <option value="">Select tier...</option>
                  <option value="1">UCI WorldTour</option>
                  <option value="2">UCI ProTeam</option>
                  <option value="3">UCI Continental</option>
                </select>
              </label>
              
              <label>
                Reason for Merge
                <textarea
                  value={formData.reason}
                  onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
                  placeholder="Explain the merger and provide sources..."
                  rows={5}
                  required
                  minLength={10}
                />
              </label>
            </div>
          )}
          
          {step === 3 && (
            <div className="step-content">
              <h3>Review Merge</h3>
              
              <div className="review-section">
                <h4>Teams Being Merged</h4>
                <ul>
                  {formData.source_nodes.map(team => {
                    const latestEra = team.eras?.[team.eras.length - 1];
                    return (
                      <li key={team.id}>
                        {latestEra?.name || 'Unknown Team'}
                      </li>
                    );
                  })}
                </ul>
              </div>
              
              <div className="review-section">
                <h4>Merge Into</h4>
                <p><strong>{formData.new_team_name}</strong></p>
                <p>Year: {formData.merge_year}</p>
                <p>Tier: {formData.new_team_tier === '1' ? 'WorldTour' : formData.new_team_tier === '2' ? 'ProTeam' : 'Continental'}</p>
              </div>
              
              <div className="review-section">
                <h4>Reason</h4>
                <p>{formData.reason}</p>
              </div>
            </div>
          )}
        </div>
        
        {error && (
          <div className="error-message">{error}</div>
        )}
        
        <div className="wizard-footer">
          {user?.role === 'NEW_USER' && (
            <div className="moderation-notice">
              <span className="notice-warning">
                ⚠️ This merge will be reviewed by moderators
              </span>
            </div>
          )}
          
          <div className="button-group">
            {step > 1 && (
              <button onClick={handleBack} disabled={submitting}>
                Back
              </button>
            )}
            <button onClick={onClose} disabled={submitting}>
              Cancel
            </button>
            {step < 3 ? (
              <button 
                onClick={handleNext}
                className="primary"
                disabled={step === 1 && formData.source_nodes.length < 2}
              >
                Next
              </button>
            ) : (
              <button 
                onClick={handleSubmit}
                className="primary"
                disabled={submitting || !formData.new_team_name || !formData.reason}
              >
                {submitting ? 'Creating...' : 'Create Merge'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
