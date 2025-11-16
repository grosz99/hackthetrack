/**
 * ProjectedRankingsTable Component
 * Shows interactive rankings table with projected position based on skill adjustments
 * THE KILLER FEATURE for the Development page
 */

import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import api from '../../services/api';
import './ProjectedRankingsTable.css';

export default function ProjectedRankingsTable({
  driverNumber,
  adjustedSkills,
  onProjectionUpdate
}) {
  const [projectionData, setProjectionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjectedRankings = async () => {
      if (!driverNumber || !adjustedSkills) return;

      try {
        setLoading(true);
        setError(null);

        const params = new URLSearchParams({
          driver_number: driverNumber,
          speed: adjustedSkills.speed,
          consistency: adjustedSkills.consistency,
          racecraft: adjustedSkills.racecraft,
          tire_management: adjustedSkills.tire_management,
        });

        const response = await api.get(`/api/rankings/projected?${params}`);
        setProjectionData(response.data);

        if (onProjectionUpdate) {
          onProjectionUpdate(response.data);
        }
      } catch (err) {
        console.error('Error fetching projected rankings:', err);
        setError('Failed to calculate projected rankings');
      } finally {
        setLoading(false);
      }
    };

    fetchProjectedRankings();
  }, [driverNumber, adjustedSkills, onProjectionUpdate]);

  if (loading) {
    return (
      <div className="projected-rankings-table loading">
        <div className="loading-spinner"></div>
        <p>Calculating projected rankings...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="projected-rankings-table error">
        <p>{error}</p>
      </div>
    );
  }

  if (!projectionData) {
    return (
      <div className="projected-rankings-table empty">
        <p>Adjust the skill sliders to see your projected ranking</p>
      </div>
    );
  }

  return (
    <div className="projected-rankings-table">
      <div className="projection-header">
        <h3>Projected Rankings</h3>
        <div className="projection-summary">
          <div className="summary-item">
            <span className="label">Current</span>
            <span className="value current">P{projectionData.current_rank}</span>
          </div>
          <div className="summary-arrow">→</div>
          <div className="summary-item">
            <span className="label">Projected</span>
            <span className="value projected">P{projectionData.projected_rank}</span>
          </div>
          <div className="positions-gained">
            {projectionData.positions_gained > 0 ? (
              <span className="gain positive">+{projectionData.positions_gained} positions</span>
            ) : projectionData.positions_gained < 0 ? (
              <span className="gain negative">{projectionData.positions_gained} positions</span>
            ) : (
              <span className="gain neutral">No change</span>
            )}
          </div>
        </div>
        <div className="confidence-badge" data-level={projectionData.confidence_level}>
          {projectionData.confidence_level.toUpperCase()} CONFIDENCE
        </div>
      </div>

      <div className="avg-finish-comparison">
        <div className="finish-item">
          <span className="finish-label">Current Avg Finish</span>
          <span className="finish-value">{projectionData.current_avg_finish.toFixed(2)}</span>
        </div>
        <div className="finish-arrow">→</div>
        <div className="finish-item">
          <span className="finish-label">Projected Avg Finish</span>
          <span className="finish-value projected">
            {projectionData.projected_avg_finish.toFixed(2)}
          </span>
        </div>
      </div>

      <div className="rankings-table-container">
        <table className="rankings-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Driver</th>
              <th>Speed</th>
              <th>Consistency</th>
              <th>Racecraft</th>
              <th>Tire Mgmt</th>
              <th>Avg Finish</th>
            </tr>
          </thead>
          <tbody>
            {projectionData.rankings_table.map((driver) => (
              <tr
                key={`${driver.driver_number}-${driver.is_projected ? 'proj' : 'curr'}`}
                className={`
                  ${driver.is_user ? 'user-row' : ''}
                  ${driver.is_projected ? 'projected-row' : ''}
                `}
              >
                <td className="rank-cell">
                  <span className="rank-number">P{driver.rank}</span>
                </td>
                <td className="driver-cell">
                  <span className="driver-name">
                    {driver.driver_name}
                    {driver.is_projected && (
                      <span className="projected-badge">NEW</span>
                    )}
                  </span>
                </td>
                <td className="skill-cell">{driver.speed.toFixed(1)}</td>
                <td className="skill-cell">{driver.consistency.toFixed(1)}</td>
                <td className="skill-cell">{driver.racecraft.toFixed(1)}</td>
                <td className="skill-cell">{driver.tire_management.toFixed(1)}</td>
                <td className="finish-cell">{driver.avg_finish.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

ProjectedRankingsTable.propTypes = {
  driverNumber: PropTypes.number.isRequired,
  adjustedSkills: PropTypes.shape({
    speed: PropTypes.number.isRequired,
    consistency: PropTypes.number.isRequired,
    racecraft: PropTypes.number.isRequired,
    tire_management: PropTypes.number.isRequired,
  }),
  onProjectionUpdate: PropTypes.func,
};

ProjectedRankingsTable.defaultProps = {
  adjustedSkills: null,
  onProjectionUpdate: null,
};
