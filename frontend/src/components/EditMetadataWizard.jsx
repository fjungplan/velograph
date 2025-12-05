import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { editsApi } from '../api/edits';
import './EditMetadataWizard.css';

export default function EditMetadataWizard({ era, onClose, onSuccess }) {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    registered_name: era.name || '',
    uci_code: era.uci_code || '',
    tier_level: era.tier || '',
    reason: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    
    try {
      // Only send changed fields
      const changes = {};
      if (formData.registered_name !== era.name) {
        changes.registered_name = formData.registered_name;
      }
      if (formData.uci_code !== era.uci_code) {
        changes.uci_code = formData.uci_code;
      }
      if (formData.tier_level && parseInt(formData.tier_level) !== era.tier) {
        changes.tier_level = parseInt(formData.tier_level);
      }
      
      if (Object.keys(changes).length === 0) {
        setError('No changes detected');
        setSubmitting(false);
        return;
      }
      
      const response = await editsApi.editMetadata({
        era_id: era.era_id,
        ...changes,
        reason: formData.reason
      });
      
      onSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit edit');
    } finally {
      setSubmitting(false);
    }
  };
  
  const isChanged = () => {
    return formData.registered_name !== era.name ||
           formData.uci_code !== era.uci_code ||
           (formData.tier_level && parseInt(formData.tier_level) !== era.tier);
  };
  
  return (
    <div className="wizard-overlay" onClick={onClose}>
      <div className="wizard-modal" onClick={(e) => e.stopPropagation()}>
        <div className="wizard-header">
          <h2>Edit Team Information</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <label>
              Team Name
              <input
                type="text"
                value={formData.registered_name}
                onChange={(e) => handleChange('registered_name', e.target.value)}
                required
              />
            </label>
            
            <label>
              UCI Code (3 letters)
              <input
                type="text"
                value={formData.uci_code}
                onChange={(e) => handleChange('uci_code', e.target.value.toUpperCase())}
                maxLength={3}
                pattern="[A-Z]{3}"
              />
            </label>
            
            <label>
              Tier Level
              <select
                value={formData.tier_level}
                onChange={(e) => handleChange('tier_level', e.target.value)}
              >
                <option value="">Select tier...</option>
                <option value="1">UCI WorldTour</option>
                <option value="2">UCI ProTeam</option>
                <option value="3">UCI Continental</option>
              </select>
            </label>
          </div>
          
          <div className="form-section">
            <label>
              Reason for Edit (required)
              <textarea
                value={formData.reason}
                onChange={(e) => handleChange('reason', e.target.value)}
                placeholder="Explain why this edit is needed..."
                rows={4}
                required
                minLength={10}
              />
            </label>
            <div className="help-text">
              Please provide a clear explanation. Include sources if available.
            </div>
          </div>
          
          {error && (
            <div className="error-message">{error}</div>
          )}
          
          <div className="wizard-footer">
            <div className="moderation-notice">
              {user?.role === 'NEW_USER' ? (
                <span className="notice-warning">
                  ⚠️ Your edit will be reviewed by moderators
                </span>
              ) : (
                <span className="notice-success">
                  ✓ Your edit will be applied immediately
                </span>
              )}
            </div>
            
            <div className="button-group">
              <button 
                type="button" 
                onClick={onClose}
                disabled={submitting}
              >
                Cancel
              </button>
              <button 
                type="submit"
                disabled={!isChanged() || !formData.reason || submitting}
                className="primary"
              >
                {submitting ? 'Submitting...' : 'Submit Edit'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
