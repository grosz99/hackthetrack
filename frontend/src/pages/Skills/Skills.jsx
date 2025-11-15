/**
 * Skills Page - 4-factor analysis with spider chart
 * NASCAR aesthetic matching Overview and RaceLog pages
 * Displays driver performance across 4 key factors
 */

import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import './Skills.css';

export default function Skills() {
  const { selectedDriverNumber, drivers } = useDriver();
  const [driverData, setDriverData] = useState(null);
  const [factorStats, setFactorStats] = useState({}); // NEW: Store factor stats from efficient endpoint
  const [selectedFactor, setSelectedFactor] = useState(null);
  const [factorBreakdown, setFactorBreakdown] = useState(null);
  const [factorComparison, setFactorComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingBreakdown, setLoadingBreakdown] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDriverData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Clear factor selection when driver changes
        setSelectedFactor(null);
        setFactorBreakdown(null);
        setFactorComparison(null);

        // Fetch current driver data and factor stats (efficient endpoint)
        const [driverResponse, ...factorResponses] = await Promise.all([
          api.get(`/api/drivers/${selectedDriverNumber}`),
          api.get('/api/factors/speed/stats'),
          api.get('/api/factors/consistency/stats'),
          api.get('/api/factors/racecraft/stats'),
          api.get('/api/factors/tire_management/stats')
        ]);

        setDriverData(driverResponse.data);

        // Store factor stats for radar chart
        setFactorStats({
          speed: factorResponses[0].data,
          consistency: factorResponses[1].data,
          racecraft: factorResponses[2].data,
          tire_management: factorResponses[3].data
        });
      } catch (err) {
        console.error('Error fetching driver data:', err);
        setError('Failed to load driver data');
      } finally {
        setLoading(false);
      }
    };

    fetchDriverData();
  }, [selectedDriverNumber]);

  if (loading) {
    return (
      <div className="skills-page">
        <div className="loading-container">
          <div className="loading-text">Loading driver skills...</div>
        </div>
      </div>
    );
  }

  if (error || !driverData) {
    return (
      <div className="skills-page">
        <div className="error-container">
          <div className="error-text">{error || 'No data available'}</div>
        </div>
      </div>
    );
  }

  // Prepare radar chart data with top 3 average from efficient endpoint
  const radarData = [
    {
      factor: 'Consistency',
      user: driverData.consistency?.percentile || 0,
      topAvg: factorStats.consistency?.top_3_average || 0,
      fullMark: 100
    },
    {
      factor: 'Racecraft',
      user: driverData.racecraft?.percentile || 0,
      topAvg: factorStats.racecraft?.top_3_average || 0,
      fullMark: 100
    },
    {
      factor: 'Raw Speed',
      user: driverData.speed?.percentile || 0,
      topAvg: factorStats.speed?.top_3_average || 0,
      fullMark: 100
    },
    {
      factor: 'Tire Mgmt',
      user: driverData.tire_management?.percentile || 0,
      topAvg: factorStats.tire_management?.top_3_average || 0,
      fullMark: 100
    },
  ];

  const handleFactorClick = async (factorName) => {
    setSelectedFactor(factorName);
    setLoadingBreakdown(true);
    setError(null);

    try {
      // Convert display name to API format (e.g., "Raw Speed" -> "speed")
      const factorNameMap = {
        'Consistency': 'consistency',
        'Racecraft': 'racecraft',
        'Raw Speed': 'speed',
        'Tire Management': 'tire_management'
      };

      const apiFactorName = factorNameMap[factorName] || factorName.toLowerCase().replace(' ', '_');

      // Fetch breakdown and comparison data in parallel
      const [breakdownResponse, comparisonResponse] = await Promise.all([
        api.get(`/api/factors/${apiFactorName}/breakdown/${selectedDriverNumber}`),
        api.get(`/api/factors/${apiFactorName}/comparison/${selectedDriverNumber}`)
      ]);

      setFactorBreakdown(breakdownResponse.data);
      setFactorComparison(comparisonResponse.data);
    } catch (err) {
      console.error('[Skills] Error loading factor breakdown:', err);
      setFactorBreakdown(null);
      setFactorComparison(null);
      setError(`Failed to load ${factorName} breakdown. Please try again later.`);
    } finally {
      setLoadingBreakdown(false);
    }
  };

  return (
    <div className="skills-page">
      {/* Unified Header with Scout Context */}
      <DashboardHeader driverData={driverData} pageName="Skills" />

      {/* Unified Navigation Tabs */}
      <DashboardTabs />

      {/* Main Content Grid - Radar Left, Factor Cards Right */}
      <div className="skills-content-new">
        {/* Radar Chart on left side */}
        <div className="radar-chart-container-new">
          <h3 className="chart-title">Performance Comparison</h3>
          <p className="chart-subtitle">You vs Top 3 Average</p>
          <ResponsiveContainer width="100%" height={500}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#ddd" strokeWidth={1} />
              <PolarAngleAxis
                dataKey="factor"
                tick={{ fill: '#000', fontSize: 16, fontWeight: 700 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fill: '#666', fontSize: 12, fontWeight: 600 }}
              />
              {/* Top 3 average in gray */}
              <Radar
                name="Top 3 Average"
                dataKey="topAvg"
                stroke="#555"
                fill="#555"
                fillOpacity={0.2}
                strokeWidth={3}
              />
              {/* Current driver in red */}
              <Radar
                name={`You (#${selectedDriverNumber})`}
                dataKey="user"
                stroke="#e74c3c"
                fill="#e74c3c"
                fillOpacity={0.4}
                strokeWidth={4}
              />
            </RadarChart>
          </ResponsiveContainer>
          <div className="radar-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ background: '#e74c3c' }}></div>
              <span>You (#{selectedDriverNumber})</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ background: '#555' }}></div>
              <span>Top 3 Average</span>
            </div>
          </div>
        </div>

        {/* Factor Cards Grid - 2x2 on right side */}
        <div className="factor-cards-container">
          <div className="factor-cards-instructions">
            <h3 className="instructions-title">Skill Factor Breakdown</h3>
            <p className="instructions-text">
              Click any skill tile below to see detailed breakdowns and comparisons with top drivers
            </p>
          </div>
          <div className="factor-cards-grid-new">
          {/* Consistency Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Consistency' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Consistency')}
          >
            <div className="factor-header">
              <h3 className="factor-name">Consistency</h3>
              <div className="factor-score">{Math.round(driverData.consistency?.score || 0)}</div>
            </div>
            <div className="factor-percentile">
              {(driverData.consistency?.percentile || 0).toFixed(1)}th Percentile
            </div>
            <div className="percentile-bar">
              <div
                className="percentile-fill"
                style={{ width: `${driverData.consistency?.percentile || 0}%` }}
              ></div>
            </div>
            <div className="factor-description">
              Measures lap-to-lap consistency and predictability of performance
            </div>
          </div>

          {/* Racecraft Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Racecraft' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Racecraft')}
          >
            <div className="factor-header">
              <h3 className="factor-name">Racecraft</h3>
              <div className="factor-score">{Math.round(driverData.racecraft?.score || 0)}</div>
            </div>
            <div className="factor-percentile">
              {(driverData.racecraft?.percentile || 0).toFixed(1)}th Percentile
            </div>
            <div className="percentile-bar">
              <div
                className="percentile-fill"
                style={{ width: `${driverData.racecraft?.percentile || 0}%` }}
              ></div>
            </div>
            <div className="factor-description">
              Ability to overtake, defend position, and navigate traffic effectively
            </div>
          </div>

          {/* Raw Speed Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Raw Speed' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Raw Speed')}
          >
            <div className="factor-header">
              <h3 className="factor-name">Raw Speed</h3>
              <div className="factor-score">{Math.round(driverData.speed?.score || 0)}</div>
            </div>
            <div className="factor-percentile">
              {(driverData.speed?.percentile || 0).toFixed(1)}th Percentile
            </div>
            <div className="percentile-bar">
              <div
                className="percentile-fill"
                style={{ width: `${driverData.speed?.percentile || 0}%` }}
              ></div>
            </div>
            <div className="factor-description">
              Pure pace and ability to extract maximum performance from the car
            </div>
          </div>

          {/* Tire Management Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Tire Management' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Tire Management')}
          >
            <div className="factor-header">
              <h3 className="factor-name">Tire Management</h3>
              <div className="factor-score">{Math.round(driverData.tire_management?.score || 0)}</div>
            </div>
            <div className="factor-percentile">
              {(driverData.tire_management?.percentile || 0).toFixed(1)}th Percentile
            </div>
            <div className="percentile-bar">
              <div
                className="percentile-fill"
                style={{ width: `${driverData.tire_management?.percentile || 0}%` }}
              ></div>
            </div>
            <div className="factor-description">
              Ability to preserve tires and maintain pace over long stints
            </div>
          </div>
          </div>
        </div>
      </div>

      {/* Variable Detail View - shown when factor is clicked */}
      {selectedFactor && (
        <div className="variable-detail-section">
          <div className="variable-detail-header">
            <h2>{selectedFactor} Breakdown</h2>
            <button className="close-button" onClick={() => setSelectedFactor(null)} aria-label="Close factor breakdown">✕</button>
          </div>

          {loadingBreakdown ? (
            <div className="loading-breakdown">
              <div className="loading-text">Loading breakdown...</div>
            </div>
          ) : factorBreakdown && factorComparison ? (
            <div className="breakdown-content">
              {/* Explanation Section */}
              <div className="explanation-box">
                <h3>What This Means</h3>
                <p>{factorBreakdown.explanation}</p>
              </div>

              {/* Variables Grid */}
              <div className="variables-grid">
                {factorBreakdown.variables.map((variable, index) => (
                  <div key={index} className="variable-card">
                    <div className="variable-header">
                      <h4>{variable.display_name}</h4>
                      <span className="variable-percentile">{variable.percentile.toFixed(1)}th</span>
                    </div>
                    <div className="variable-bar">
                      <div
                        className="variable-bar-fill"
                        style={{ width: `${variable.normalized_value}%` }}
                      ></div>
                    </div>
                    <div className="variable-stats">
                      <span className="variable-score">{variable.normalized_value.toFixed(1)}/100</span>
                      <span className="variable-weight">Weight: {(variable.weight * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Comparison Section */}
              <div className="comparison-section">
                <h3>How You Stack Up</h3>
                <div className="comparison-grid">
                  {/* User Driver */}
                  <div className="driver-comparison-card user-card">
                    <div className="card-header">
                      <span className="driver-label">You</span>
                      <span className="driver-number">#{factorComparison.user_driver.driver_number}</span>
                    </div>
                    <div className="driver-score">{factorComparison.user_driver.percentile.toFixed(1)}th percentile</div>
                    <div className="mini-bars">
                      {factorBreakdown.variables.map((variable, idx) => (
                        <div key={idx} className="mini-bar-row">
                          <span className="mini-label">{variable.display_name}</span>
                          <div className="mini-bar">
                            <div
                              className="mini-bar-fill user-fill"
                              style={{ width: `${factorComparison.user_driver.variables[variable.name]}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Top 3 Drivers */}
                  {factorComparison.top_drivers.map((driver, idx) => (
                    <div key={idx} className="driver-comparison-card">
                      <div className="card-header">
                        <span className="driver-label">#{idx + 1} Best</span>
                        <span className="driver-number">#{driver.driver_number}</span>
                      </div>
                      <div className="driver-score">{driver.percentile.toFixed(1)}th percentile</div>
                      <div className="mini-bars">
                        {factorBreakdown.variables.map((variable, vidx) => (
                          <div key={vidx} className="mini-bar-row">
                            <span className="mini-label">{variable.display_name}</span>
                            <div className="mini-bar">
                              <div
                                className="mini-bar-fill"
                                style={{ width: `${driver.variables[variable.name]}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Insights */}
                <div className="insights-box">
                  <h4>Key Insights</h4>
                  <ul className="insights-list">
                    {factorComparison.insights.map((insight, idx) => (
                      <li key={idx}>{insight}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="error-breakdown">
              <p>Unable to load factor breakdown. Please try again.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
