import React from 'react';
/**
 * Race Log Page - Race-by-race results with NASCAR aesthetic
 * Matches the Tyler Maxson style from Overview page
 */

import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import './RaceLog.css';

export default function RaceLog() {
  const { selectedDriverNumber, drivers } = useDriver();
  const [raceResults, setRaceResults] = useState([]);
  const [driverData, setDriverData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: 'round', direction: 'asc' });
  const [expandedRound, setExpandedRound] = useState(null);

  useEffect(() => {
    const fetchRaceResults = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch both race results and driver data
        const [resultsResponse, driverResponse] = await Promise.all([
          api.get(`/api/drivers/${selectedDriverNumber}/results`),
          api.get(`/api/drivers/${selectedDriverNumber}`)
        ]);

        setRaceResults(resultsResponse.data);
        setDriverData(driverResponse.data);
      } catch (err) {
        console.error('Error fetching race results:', err);
        setError('Failed to load race results');
      } finally {
        setLoading(false);
      }
    };

    fetchRaceResults();
  }, [selectedDriverNumber]);

  // Sort race results
  const sortedResults = [...raceResults].sort((a, b) => {
    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];

    if (aValue === null || aValue === undefined) return 1;
    if (bValue === null || bValue === undefined) return -1;

    if (sortConfig.direction === 'asc') {
      return aValue > bValue ? 1 : -1;
    }
    return aValue < bValue ? 1 : -1;
  });

  const handleSort = (key) => {
    setSortConfig((prevConfig) => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  // Calculate season averages
  const calculateAverages = () => {
    if (raceResults.length === 0) {
      return { avgStart: 0, avgFinish: 0, avgGain: 0 };
    }

    const totals = raceResults.reduce((acc, result) => {
      const gain = (result.start_position - result.finish_position) || 0;
      return {
        start: acc.start + (result.start_position || 0),
        finish: acc.finish + (result.finish_position || 0),
        gain: acc.gain + gain,
      };
    }, { start: 0, finish: 0, gain: 0 });

    return {
      avgStart: (totals.start / raceResults.length).toFixed(1),
      avgFinish: (totals.finish / raceResults.length).toFixed(1),
      avgGain: (totals.gain / raceResults.length).toFixed(1),
    };
  };

  const averages = calculateAverages();

  const toggleRoundExpansion = (round) => {
    setExpandedRound(expandedRound === round ? null : round);
  };

  const renderPositionChange = (change) => {
    if (change === null || change === undefined || change === 0) {
      return <span className="position-change neutral">—</span>;
    }

    if (change > 0) {
      return (
        <span className="position-change positive">
          ↑ {change}
        </span>
      );
    }

    return (
      <span className="position-change negative">
        ↓ {Math.abs(change)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="race-log-page">
        <div className="loading-container">
          <div className="loading-text">Loading race results...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="race-log-page">
        <div className="error-container">
          <div className="error-text">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="race-log-page">
      {/* Unified Header with Scout Context */}
      <DashboardHeader driverData={driverData} pageName="Race Log" />

      {/* Unified Navigation Tabs */}
      <DashboardTabs />

      {/* OLD HEADER - REMOVE */}
      <div className="race-log-header" style={{ display: 'none' }}>
        <div className="header-content">
          <div className="driver-number-display">
            <span className="number-large">{selectedDriverNumber}</span>
          </div>
          <div className="driver-name-section">
            <h1 className="driver-name">Driver #{selectedDriverNumber}</h1>
            <div className="season-subtitle">Toyota Gazoo Series</div>
          </div>

          {/* Driver Selector */}
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{
              fontSize: '18px',
              fontWeight: 700,
              color: '#fff',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Select Driver
            </span>
            <select
              value={selectedDriverNumber}
              onChange={(e) => console.log('Old selector - should not be used')}
              style={{
                padding: '12px 20px',
                fontSize: '16px',
                fontWeight: 700,
                background: '#fff',
                color: '#000',
                border: '4px solid #e74c3c',
                borderRadius: '12px',
                cursor: 'pointer',
                outline: 'none',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 16px rgba(231, 76, 60, 0.3)',
                minWidth: '200px',
                fontFamily: 'Inter, sans-serif',
                appearance: 'none',
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L6 6L11 1' stroke='%23e74c3c' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E")`,
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'right 16px center',
                paddingRight: '48px'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 24px rgba(231, 76, 60, 0.4)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(231, 76, 60, 0.3)';
              }}
            >
              {drivers.map((driver) => (
                <option key={driver.number} value={driver.number}>
                  {driver.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* OLD NAV TABS - REMOVE */}
      <div className="nav-tabs-container" style={{ display: 'none' }}>
      </div>

      {/* Season Averages */}
      <div className="season-averages">
        <h3 className="averages-title">Season Averages</h3>
        <div className="averages-grid">
          <div className="average-stat">
            <div className="average-value">{averages.avgStart}</div>
            <div className="average-label">Avg Start Position</div>
          </div>
          <div className="average-stat">
            <div className="average-value">{averages.avgFinish}</div>
            <div className="average-label">Avg Finish Position</div>
          </div>
          <div className="average-stat">
            <div className="average-value" style={{
              color: averages.avgGain > 0 ? '#2ecc71' : averages.avgGain < 0 ? '#e74c3c' : '#888'
            }}>
              {averages.avgGain > 0 ? '+' : ''}{averages.avgGain}
            </div>
            <div className="average-label">Avg Position Gain</div>
          </div>
        </div>
      </div>

      {/* Race Results Table */}
      <div className="race-table-container">
        <div className="table-header">
          <h2 className="table-title">2025 Season Results</h2>
          <div className="table-subtitle">Click rows for race lap time analysis</div>
        </div>

        <table className="race-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('round')} style={{ cursor: 'pointer' }}>
                Round {sortConfig.key === 'round' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('track_name')} style={{ cursor: 'pointer' }}>
                Track {sortConfig.key === 'track_name' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('qualifying_time')} style={{ cursor: 'pointer' }}>
                Qualifying Time {sortConfig.key === 'qualifying_time' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('gap_to_pole')} style={{ cursor: 'pointer' }}>
                Gap to Pole {sortConfig.key === 'gap_to_pole' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('start_position')} style={{ cursor: 'pointer' }}>
                Start {sortConfig.key === 'start_position' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('finish_position')} style={{ cursor: 'pointer' }}>
                Finish {sortConfig.key === 'finish_position' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th>Change</th>
              <th onClick={() => handleSort('gap_to_winner')} style={{ cursor: 'pointer' }}>
                Gap to Winner {sortConfig.key === 'gap_to_winner' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedResults.map((result, index) => {
              const positionChange = (result.start_position - result.finish_position) || 0;
              const isExpanded = expandedRound === result.round;

              return (
                <>
                  <tr
                    key={index}
                    onClick={() => toggleRoundExpansion(result.round)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>{result.round} {isExpanded ? '▼' : '▶'}</td>
                    <td className="track-name">{result.track_name || 'N/A'}</td>
                    <td className="fastest-lap">{result.qualifying_time || '—'}</td>
                    <td className="gap-to-winner">{result.gap_to_pole || '—'}</td>
                    <td className="position">{result.start_position || '—'}</td>
                    <td className="position">{result.finish_position || '—'}</td>
                    <td>{renderPositionChange(positionChange)}</td>
                    <td className="gap-to-winner">{result.gap_to_winner || '—'}</td>
                  </tr>

                  {isExpanded && (
                    <tr key={`${index}-expanded`} className="expanded-row">
                      <td colSpan="8">
                        <div className="expanded-details">
                          <div className="detail-section">
                            <div className="detail-label">Driver Fastest Lap</div>
                            <div className="detail-value">{result.driver_fastest_lap || '—'}</div>
                          </div>
                          <div className="detail-section">
                            <div className="detail-label">Gap to Fastest Lap</div>
                            <div className="detail-value" style={{
                              color: result.gap_to_fastest_lap === '0.000' ? '#2ecc71' : '#e74c3c'
                            }}>
                              {result.gap_to_fastest_lap || '—'}
                            </div>
                          </div>
                          <div className="detail-section">
                            <div className="detail-label">Driver S1 Best</div>
                            <div className="detail-value">{result.driver_s1_best || '—'}</div>
                          </div>
                          <div className="detail-section">
                            <div className="detail-label">Gap to S1 Best</div>
                            <div className="detail-value" style={{
                              color: result.gap_to_s1_best === '0.000' ? '#2ecc71' : '#e74c3c'
                            }}>
                              {result.gap_to_s1_best || '—'}
                            </div>
                          </div>
                          <div className="detail-section">
                            <div className="detail-label">Driver S2 Best</div>
                            <div className="detail-value">{result.driver_s2_best || '—'}</div>
                          </div>
                          <div className="detail-section">
                            <div className="detail-label">Gap to S2 Best</div>
                            <div className="detail-value" style={{
                              color: result.gap_to_s2_best === '0.000' ? '#2ecc71' : '#e74c3c'
                            }}>
                              {result.gap_to_s2_best || '—'}
                            </div>
                          </div>
                          <div className="detail-section">
                            <div className="detail-label">Driver S3 Best</div>
                            <div className="detail-value">{result.driver_s3_best || '—'}</div>
                          </div>
                          <div className="detail-section">
                            <div className="detail-label">Gap to S3 Best</div>
                            <div className="detail-value" style={{
                              color: result.gap_to_s3_best === '0.000' ? '#2ecc71' : '#e74c3c'
                            }}>
                              {result.gap_to_s3_best || '—'}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
