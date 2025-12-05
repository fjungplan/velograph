import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { editsApi } from '../api/edits';
import './SplitWizard.css';

export default function SplitWizard({ sourceNode, onClose, onSuccess }) {
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    split_year: new Date().getFullYear(),
    new_teams: [
      { name: '', tier: '' },
      { name: '', tier: '' }
    ],
    reason: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const addNewTeam = () => {
    if (formData.new_teams.length >= 5) {
      setError('Maximum 5 teams can result from a split');
      return;
    }

    setFormData(prev => ({
      ...prev,
      new_teams: [...prev.new_teams, { name: '', tier: '' }]
    }));
    setError(null);
  };

  const removeNewTeam = (index) => {
    if (formData.new_teams.length <= 2) {
      setError('Split must result in at least 2 teams');
      return;
    }

    setFormData(prev => ({
      ...prev,
      new_teams: prev.new_teams.filter((_, i) => i !== index)
    }));
    setError(null);
  };

  const updateNewTeam = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      new_teams: prev.new_teams.map((team, i) =>
        i === index ? { ...team, [field]: value } : team
      )
    }));
  };

  const isStepValid = () => {
    if (step === 1) {
      return formData.new_teams.every(team => team.name && team.tier);
    }
    if (step === 2) {
      return formData.reason.length >= 10;
    }
    return true;
  };

  const handleNext = () => {
    if (!isStepValid()) {
      setError('Please fill in all required fields');
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
      const response = await editsApi.createSplit({
        source_node_id: sourceNode.id,
        split_year: parseInt(formData.split_year),
        new_teams: formData.new_teams.map(team => ({
          name: team.name,
          tier: parseInt(team.tier)
        })),
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
        setError('Failed to create split. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="wizard-overlay" onClick={onClose}>
      <div className="wizard-modal large" onClick={(e) => e.stopPropagation()}>
        <div className="wizard-header">
          <h2>Create Team Split</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="wizard-progress">
          <div className={`step ${step >= 1 ? 'active' : ''}`}>1. New Teams</div>
          <div className={`step ${step >= 2 ? 'active' : ''}`}>2. Details</div>
          <div className={`step ${step >= 3 ? 'active' : ''}`}>3. Review</div>
        </div>

        <div className="wizard-content">
          {step === 1 && (
            <div className="step-content">
              <h3>Define Resulting Teams</h3>
              <p>Splitting: <strong>{sourceNode.eras[sourceNode.eras.length - 1].name}</strong></p>

              <div className="new-teams-list">
                {formData.new_teams.map((team, index) => (
                  <div key={index} className="new-team-form">
                    <h4>Team {index + 1}</h4>
                    <label>
                      Team Name
                      <input
                        type="text"
                        value={team.name}
                        onChange={(e) => updateNewTeam(index, 'name', e.target.value)}
                        placeholder="e.g., Team Jumbo-Visma"
                        required
                      />
                    </label>

                    <label>
                      Tier
                      <select
                        value={team.tier}
                        onChange={(e) => updateNewTeam(index, 'tier', e.target.value)}
                        required
                      >
                        <option value="">Select tier...</option>
                        <option value="1">UCI WorldTour</option>
                        <option value="2">UCI ProTeam</option>
                        <option value="3">UCI Continental</option>
                      </select>
                    </label>

                    {formData.new_teams.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeNewTeam(index)}
                        className="remove-button"
                      >
                        Remove Team
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {formData.new_teams.length < 5 && (
                <button
                  type="button"
                  onClick={addNewTeam}
                  className="add-team-button"
                >
                  + Add Another Team
                </button>
              )}
            </div>
          )}

          {step === 2 && (
            <div className="step-content">
              <h3>Split Details</h3>

              <label>
                Split Year
                <input
                  type="number"
                  value={formData.split_year}
                  onChange={(e) => setFormData(prev => ({ ...prev, split_year: e.target.value }))}
                  min={1900}
                  max={new Date().getFullYear() + 1}
                  required
                />
              </label>

              <label>
                Reason for Split
                <textarea
                  value={formData.reason}
                  onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
                  placeholder="Explain why the team split and provide sources..."
                  rows={6}
                  required
                  minLength={10}
                />
              </label>
            </div>
          )}

          {step === 3 && (
            <div className="step-content">
              <h3>Review Split</h3>

              <div className="review-section">
                <h4>Source Team</h4>
                <p><strong>{sourceNode.eras[sourceNode.eras.length - 1].name}</strong></p>
                <p>Will be dissolved in {formData.split_year}</p>
              </div>

              <div className="review-section">
                <h4>Resulting Teams</h4>
                <ul>
                  {formData.new_teams.map((team, index) => (
                    <li key={index}>
                      <strong>{team.name}</strong>
                      {' - '}
                      {team.tier === '1' ? 'WorldTour' : team.tier === '2' ? 'ProTeam' : 'Continental'}
                    </li>
                  ))}
                </ul>
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
                ⚠️ This split will be reviewed by moderators
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
                disabled={!isStepValid()}
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                className="primary"
                disabled={submitting}
              >
                {submitting ? 'Creating...' : 'Create Split'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
