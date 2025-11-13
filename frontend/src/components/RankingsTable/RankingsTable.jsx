import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import './RankingsTable.css';

export default function RankingsTable({ drivers = [] }) {
  const navigate = useNavigate();
  const [sortKey, setSortKey] = useState('overall_score');
  const [sortDirection, setSortDirection] = useState('desc');

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
        <h1 className="rankings-title">DRIVER RANKINGS</h1>
        <p className="rankings-subtitle">Development Pool - 4 Factor Performance Model</p>
      </div>

      <div className="table-wrapper">
        <table className="rankings-table">
          <thead>
            <tr>
              <th>DRIVER</th>
              <th onClick={() => handleSort('overall_score')} className="sortable">
                OVERALL {sortKey === 'overall_score' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('cornering')} className="sortable">
                CORNERING {sortKey === 'cornering' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('tire_mgmt')} className="sortable">
                TIRE MGMT {sortKey === 'tire_mgmt' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('racecraft')} className="sortable">
                RACECRAFT {sortKey === 'racecraft' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('raw_speed')} className="sortable">
                RAW SPEED {sortKey === 'raw_speed' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('wins')} className="sortable">
                WINS {sortKey === 'wins' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('top10')} className="sortable">
                TOP 10 {sortKey === 'top10' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('dnfs')} className="sortable">
                DNF {sortKey === 'dnfs' && (sortDirection === 'asc' ? '↑' : '↓')}
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

                {/* DNF */}
                <td>
                  <span className="stat-value">{driver.dnfs}</span>
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
