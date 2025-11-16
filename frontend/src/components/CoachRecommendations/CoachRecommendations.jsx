/**
 * CoachRecommendations Component
 * Displays actionable coaching recommendations with telemetry-backed evidence
 */

import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import api from '../../services/api';
import './CoachRecommendations.css';

export default function CoachRecommendations({ driverNumber }) {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedRec, setExpandedRec] = useState(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!driverNumber) return;

      try {
        setLoading(true);
        setError(null);
        const response = await api.get(`/api/drivers/${driverNumber}/coach-recommendations`);
        setRecommendations(response.data);
      } catch (err) {
        console.error('Error fetching coach recommendations:', err);
        setError('Failed to load coaching recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [driverNumber]);

  if (loading) {
    return (
      <div className="coach-recommendations loading">
        <div className="loading-spinner"></div>
        <p>Generating coaching recommendations...</p>
      </div>
    );
  }

  if (error || !recommendations) {
    return (
      <div className="coach-recommendations error">
        <p>{error || 'No recommendations available'}</p>
      </div>
    );
  }

  return (
    <div className="coach-recommendations">
      <div className="recommendations-header">
        <h3>Coach Recommendations</h3>
        <p className="summary">{recommendations.summary}</p>
      </div>

      <div className="recommendations-list">
        {recommendations.recommendations.length === 0 ? (
          <div className="no-recommendations">
            No specific recommendations at this time. You're performing at top level!
          </div>
        ) : (
          recommendations.recommendations.map((rec) => (
            <div
              key={rec.priority}
              className={`recommendation-card priority-${rec.priority} ${
                expandedRec === rec.priority ? 'expanded' : ''
              }`}
              onClick={() => setExpandedRec(expandedRec === rec.priority ? null : rec.priority)}
              role="button"
              tabIndex={0}
              aria-expanded={expandedRec === rec.priority}
              aria-label={`Recommendation ${rec.priority}: ${rec.skill_area}`}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setExpandedRec(expandedRec === rec.priority ? null : rec.priority);
                }
              }}
            >
              <div className="rec-header">
                <div className="priority-circle">
                  <span>{rec.priority}</span>
                </div>
                <div className="rec-title">
                  <h4>{rec.skill_area}</h4>
                  <span className="improvement-badge">{rec.expected_improvement}</span>
                </div>
              </div>

              <div className="rec-content">
                <p className="rec-text">{rec.recommendation}</p>
              </div>

              {expandedRec === rec.priority && rec.evidence.length > 0 && (
                <div className="evidence-section">
                  <h5>Telemetry Evidence</h5>
                  <ul className="evidence-list">
                    {rec.evidence.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="expand-hint">
                {expandedRec === rec.priority ? 'Click to collapse' : 'Click for evidence'}
              </div>
            </div>
          ))
        )}
      </div>

      {Object.keys(recommendations.track_specific_insights).length > 0 && (
        <div className="track-insights-section">
          <h4>Track-Specific Insights</h4>
          {Object.entries(recommendations.track_specific_insights).map(([track, insights]) => (
            <div key={track} className="track-insights">
              <h5>{track.charAt(0).toUpperCase() + track.slice(1)}</h5>
              <ul>
                {insights.slice(0, 3).map((insight, idx) => (
                  <li key={idx}>{insight}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

CoachRecommendations.propTypes = {
  driverNumber: PropTypes.number.isRequired,
};
