/**
 * SkillGapPrioritizer Component
 * Shows prioritized skill gaps with position impact and telemetry evidence
 * Core component for the Driver's Coach View
 */

import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import api from '../../services/api';
import './SkillGapPrioritizer.css';

export default function SkillGapPrioritizer({ driverNumber, onGapSelected }) {
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedGap, setExpandedGap] = useState(null);

  useEffect(() => {
    const fetchSkillGaps = async () => {
      if (!driverNumber) return;

      try {
        setLoading(true);
        setError(null);
        const response = await api.get(`/api/drivers/${driverNumber}/skill-gaps`);
        setGapData(response.data);
      } catch (err) {
        console.error('Error fetching skill gaps:', err);
        setError('Failed to load skill gap analysis');
      } finally {
        setLoading(false);
      }
    };

    fetchSkillGaps();
  }, [driverNumber]);

  const handleGapClick = (gap) => {
    setExpandedGap(expandedGap === gap.factor_name ? null : gap.factor_name);
    if (onGapSelected) {
      onGapSelected(gap);
    }
  };

  if (loading) {
    return (
      <div className="skill-gap-prioritizer loading">
        <div className="loading-spinner"></div>
        <p>Analyzing skill gaps...</p>
      </div>
    );
  }

  if (error || !gapData) {
    return (
      <div className="skill-gap-prioritizer error">
        <p>{error || 'No data available'}</p>
      </div>
    );
  }

  return (
    <div className="skill-gap-prioritizer">
      <div className="prioritizer-header">
        <h3>Prioritized Weakness Analysis</h3>
        <div className="rank-info">
          <span className="current-rank">Current: P{gapData.current_overall_rank}</span>
          <span className="arrow">→</span>
          <span className="potential-rank">Potential: P{gapData.estimated_potential_rank}</span>
        </div>
      </div>

      <div className="coach-summary">
        <p>{gapData.coach_summary}</p>
      </div>

      <div className="skill-gaps-list">
        {gapData.skill_gaps.length === 0 ? (
          <div className="no-gaps">
            Excellent! You're performing at or above top 3 level in all areas.
          </div>
        ) : (
          gapData.skill_gaps.map((gap) => (
            <div
              key={gap.factor_name}
              className={`skill-gap-card priority-${gap.priority_rank} ${
                expandedGap === gap.factor_name ? 'expanded' : ''
              }`}
              onClick={() => handleGapClick(gap)}
              role="button"
              tabIndex={0}
              aria-expanded={expandedGap === gap.factor_name}
              aria-label={`${gap.display_name} - Priority ${gap.priority_rank} - ${gap.position_impact.toFixed(1)} positions potential improvement`}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleGapClick(gap);
                }
              }}
            >
              <div className="gap-header">
                <div className="priority-badge">P{gap.priority_rank}</div>
                <div className="gap-title">
                  <h4>{gap.display_name}</h4>
                  <span className="impact-badge">+{gap.position_impact.toFixed(1)} positions</span>
                </div>
              </div>

              <div className="gap-metrics">
                <div className="metric">
                  <span className="label">Your Score</span>
                  <span className="value">{gap.current_percentile.toFixed(1)}th</span>
                </div>
                <div className="metric gap-arrow">
                  <span className="arrow-icon">→</span>
                  <span className="gap-value">-{gap.gap_percentile.toFixed(1)} pts</span>
                </div>
                <div className="metric">
                  <span className="label">Top 3 Avg</span>
                  <span className="value target">{gap.top3_average.toFixed(1)}th</span>
                </div>
              </div>

              <div className="gap-bar-container">
                <div className="gap-bar">
                  <div
                    className="current-bar"
                    style={{ width: `${gap.current_percentile}%` }}
                  ></div>
                  <div
                    className="target-marker"
                    style={{ left: `${gap.top3_average}%` }}
                  ></div>
                </div>
              </div>

              {/* Telemetry Evidence (collapsible) */}
              {expandedGap === gap.factor_name && gap.telemetry_evidence.length > 0 && (
                <div className="telemetry-evidence">
                  <h5>Telemetry Evidence (Barber)</h5>
                  <ul>
                    {gap.telemetry_evidence.map((evidence, idx) => (
                      <li key={idx}>{evidence}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="click-hint">
                {expandedGap === gap.factor_name ? 'Click to collapse' : 'Click for details'}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

SkillGapPrioritizer.propTypes = {
  driverNumber: PropTypes.number.isRequired,
  onGapSelected: PropTypes.func,
};

SkillGapPrioritizer.defaultProps = {
  onGapSelected: null,
};
