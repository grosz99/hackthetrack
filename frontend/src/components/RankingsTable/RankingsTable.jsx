import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import ToyotaGibbsLogo from '../ToyotaGibbsLogo/ToyotaGibbsLogo';
import { TrophyIcon } from '../icons';
import './RankingsTable.css';

export default function RankingsTable({ drivers = [], onShowInfo }) {
  const navigate = useNavigate();
  const [sortKey, setSortKey] = useState('overall_score');
  const [sortDirection, setSortDirection] = useState('desc');
  const [activeTooltip, setActiveTooltip] = useState(null);

  // Metric explanations (2 sentences max)
  const metricInfo = {
    overall_score: "Weighted composite of all four performance factors. Speed 46.6%, Consistency 29.1%, Racecraft 14.9%, Tire Management 9.5%.",
    cornering: "Measures consistency through lap time standard deviation and position variability. Lower variation indicates more reliable, predictable performance.",
    tire_mgmt: "Evaluates pace maintenance across race distance by comparing early vs late lap times. Positive values show drivers who get faster as tires wear.",
    racecraft: "Assesses overtaking ability and defensive skills through position changes and battles won. Captures wheel-to-wheel racing prowess.",
    raw_speed: "Pure pace measured by fastest lap times and qualifying positions. The foundation of competitive performance.",
    wins: "Total race victories. The ultimate measure of on-track success.",
    top10: "Number of top-10 finishes. Indicates consistency in points-scoring positions."
  };

  // Calculate overall score from 4 factors using validated coefficients
  // Coefficients from statistical validation (see backend routes.py lines 740-746)
  const getOverallScore = (driver) => {
    const { speed, consistency, racecraft, tire_management } = driver;
    const weights = {
      speed: 0.466,         // 46.6% - Most important factor
      consistency: 0.291,   // 29.1%
      racecraft: 0.149,     // 14.9%
      tire_management: 0.095 // 9.5%
    };

    const weightedScore = (
      (speed * weights.speed) +
      (consistency * weights.consistency) +
      (racecraft * weights.racecraft) +
      (tire_management * weights.tire_management)
    );

    return Math.round(weightedScore);
  };

  // Add ranking and stats to drivers
  const enrichedDrivers = drivers.map(driver => {
    // DriverContext already flattens the data, so we can use it directly
    // It maps: driver_number -> number, driver_name -> name, speed.score -> speed, etc.
    return {
      ...driver,
      // These are already in correct format from DriverContext
      overall_score: driver.overall_score || getOverallScore(driver),
      cornering: driver.racecraft || 0,  // Already the score value
      tire_mgmt: driver.tire_management || 0,  // Already the score value
      raw_speed: driver.speed || 0,  // Already the score value
      // Stats are already mapped: wins, top10, dnfs
    };
  });

  // Sort drivers
  const sortedDrivers = [...enrichedDrivers].sort((a, b) => {
    let aVal = a[sortKey] || 0;
    let bVal = b[sortKey] || 0;

    if (sortDirection === 'asc') {
      return aVal - bVal;
    }
    return bVal - aVal;
  });

  // Add rank based on overall score
  const rankedDrivers = sortedDrivers.map((driver, index) => ({
    ...driver,
    rank: index + 1,
  }));

  const handleSort = (key) => {
    if (sortKey === key) {
      // Toggle direction
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New sort key, default to descending (higher is better)
      setSortKey(key);
      setSortDirection('desc');
    }
  };

  const handleDriverClick = (driverNumber) => {
    navigate(`/driver/${driverNumber}/overview`);
  };

  const getPercentileColor = (value) => {
    if (value >= 75) return 'var(--color-success)';
    if (value >= 50) return 'var(--color-warning)';
    return 'var(--color-danger)';
  };

  return (
    <div className="rankings-table-container">
      <div className="rankings-header">
        <div className="rankings-header-content">
          <div className="rankings-center-section">
            <div className="rankings-icon">
              <TrophyIcon size="lg" />
            </div>
            <div className="rankings-title-section">
              <h1 className="rankings-title">DRIVER RANKINGS</h1>
              {onShowInfo && (
                <button className="info-modal-button" onClick={onShowInfo} aria-label="Learn about the platform">
                  Platform Overview
                </button>
              )}
            </div>
          </div>
          <div className="rankings-logo-container">
            <ToyotaGibbsLogo size="large" />
          </div>
        </div>
        <div className="rankings-description">
          <p className="description-text">
            <strong>Click on any driver</strong> to view their complete performance dashboard with detailed analytics, race logs, skills breakdown, and personalized improvement recommendations
          </p>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="rankings-table">
          <thead>
            <tr>
              <th>DRIVER</th>
              <th
                className="sortable-with-info"
                onMouseEnter={() => setActiveTooltip('overall_score')}
                onMouseLeave={() => setActiveTooltip(null)}
                onClick={() => handleSort('overall_score')}
              >
                <div className="header-content">
                  OVERALL {sortKey === 'overall_score' && (sortDirection === 'asc' ? '↑' : '↓')}
                  {activeTooltip === 'overall_score' && (
                    <div className="tooltip">{metricInfo.overall_score}</div>
                  )}
                </div>
              </th>
              <th
                className="sortable-with-info"
                onMouseEnter={() => setActiveTooltip('cornering')}
                onMouseLeave={() => setActiveTooltip(null)}
                onClick={() => handleSort('cornering')}
              >
                <div className="header-content">
                  CORNERING {sortKey === 'cornering' && (sortDirection === 'asc' ? '↑' : '↓')}
                  {activeTooltip === 'cornering' && (
                    <div className="tooltip">{metricInfo.cornering}</div>
                  )}
                </div>
              </th>
              <th
                className="sortable-with-info"
                onMouseEnter={() => setActiveTooltip('tire_mgmt')}
                onMouseLeave={() => setActiveTooltip(null)}
                onClick={() => handleSort('tire_mgmt')}
              >
                <div className="header-content">
                  TIRE MGMT {sortKey === 'tire_mgmt' && (sortDirection === 'asc' ? '↑' : '↓')}
                  {activeTooltip === 'tire_mgmt' && (
                    <div className="tooltip">{metricInfo.tire_mgmt}</div>
                  )}
                </div>
              </th>
              <th
                className="sortable-with-info"
                onMouseEnter={() => setActiveTooltip('racecraft')}
                onMouseLeave={() => setActiveTooltip(null)}
                onClick={() => handleSort('racecraft')}
              >
                <div className="header-content">
                  RACECRAFT {sortKey === 'racecraft' && (sortDirection === 'asc' ? '↑' : '↓')}
                  {activeTooltip === 'racecraft' && (
                    <div className="tooltip">{metricInfo.racecraft}</div>
                  )}
                </div>
              </th>
              <th
                className="sortable-with-info"
                onMouseEnter={() => setActiveTooltip('raw_speed')}
                onMouseLeave={() => setActiveTooltip(null)}
                onClick={() => handleSort('raw_speed')}
              >
                <div className="header-content">
                  RAW SPEED {sortKey === 'raw_speed' && (sortDirection === 'asc' ? '↑' : '↓')}
                  {activeTooltip === 'raw_speed' && (
                    <div className="tooltip">{metricInfo.raw_speed}</div>
                  )}
                </div>
              </th>
              <th
                className="sortable-with-info"
                onMouseEnter={() => setActiveTooltip('wins')}
                onMouseLeave={() => setActiveTooltip(null)}
                onClick={() => handleSort('wins')}
              >
                <div className="header-content">
                  WINS {sortKey === 'wins' && (sortDirection === 'asc' ? '↑' : '↓')}
                  {activeTooltip === 'wins' && (
                    <div className="tooltip">{metricInfo.wins}</div>
                  )}
                </div>
              </th>
              <th
                className="sortable-with-info"
                onMouseEnter={() => setActiveTooltip('top10')}
                onMouseLeave={() => setActiveTooltip(null)}
                onClick={() => handleSort('top10')}
              >
                <div className="header-content">
                  TOP 10 {sortKey === 'top10' && (sortDirection === 'asc' ? '↑' : '↓')}
                  {activeTooltip === 'top10' && (
                    <div className="tooltip">{metricInfo.top10}</div>
                  )}
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {rankedDrivers.map((driver, index) => (
              <motion.tr
                key={driver.number}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.03, duration: 0.3 }}
                onClick={() => handleDriverClick(driver.number)}
                className="driver-row"
              >
                {/* Driver Info */}
                <td className="driver-info">
                  <div className="driver-number-badge">{driver.number}</div>
                  <span className="driver-name">{driver.name}</span>
                </td>

                {/* Overall Score */}
                <td>
                  <div className="score-cell">
                    <span className="score-value">{Math.round(driver.overall_score)}</span>
                  </div>
                </td>

                {/* Cornering */}
                <td>
                  <div className="factor-cell">
                    <span className="factor-value">{Math.round(driver.cornering)}</span>
                    <div className="progress-bar-container">
                      <motion.div
                        className="progress-bar"
                        style={{ backgroundColor: getPercentileColor(driver.cornering) }}
                        initial={{ width: 0 }}
                        animate={{ width: `${driver.cornering}%` }}
                        transition={{ delay: index * 0.03 + 0.2, duration: 0.6 }}
                      />
                    </div>
                  </div>
                </td>

                {/* Tire Management */}
                <td>
                  <div className="factor-cell">
                    <span className="factor-value">{Math.round(driver.tire_mgmt)}</span>
                    <div className="progress-bar-container">
                      <motion.div
                        className="progress-bar"
                        style={{ backgroundColor: getPercentileColor(driver.tire_mgmt) }}
                        initial={{ width: 0 }}
                        animate={{ width: `${driver.tire_mgmt}%` }}
                        transition={{ delay: index * 0.03 + 0.25, duration: 0.6 }}
                      />
                    </div>
                  </div>
                </td>

                {/* Racecraft */}
                <td>
                  <div className="factor-cell">
                    <span className="factor-value">{Math.round(driver.racecraft)}</span>
                    <div className="progress-bar-container">
                      <motion.div
                        className="progress-bar"
                        style={{ backgroundColor: getPercentileColor(driver.racecraft) }}
                        initial={{ width: 0 }}
                        animate={{ width: `${driver.racecraft}%` }}
                        transition={{ delay: index * 0.03 + 0.3, duration: 0.6 }}
                      />
                    </div>
                  </div>
                </td>

                {/* Raw Speed */}
                <td>
                  <div className="factor-cell">
                    <span className="factor-value">{Math.round(driver.raw_speed)}</span>
                    <div className="progress-bar-container">
                      <motion.div
                        className="progress-bar"
                        style={{ backgroundColor: getPercentileColor(driver.raw_speed) }}
                        initial={{ width: 0 }}
                        animate={{ width: `${driver.raw_speed}%` }}
                        transition={{ delay: index * 0.03 + 0.35, duration: 0.6 }}
                      />
                    </div>
                  </div>
                </td>

                {/* Wins */}
                <td>
                  <span className="stat-value">{driver.wins}</span>
                </td>

                {/* Top 10 */}
                <td>
                  <span className="stat-value">{driver.top10}</span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {rankedDrivers.length === 0 && (
        <div className="no-drivers">
          <p>No drivers found</p>
        </div>
      )}
    </div>
  );
}
