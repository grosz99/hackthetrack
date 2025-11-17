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
import SkillGapPrioritizer from '../../components/SkillGapPrioritizer/SkillGapPrioritizer';
import CoachRecommendations from '../../components/CoachRecommendations/CoachRecommendations';
import './Skills.css';

export default function Skills() {
  const { selectedDriverNumber, drivers } = useDriver();
  const [driverData, setDriverData] = useState(null);
  const [factorStats, setFactorStats] = useState({}); // NEW: Store factor stats from efficient endpoint
  const [allVariables, setAllVariables] = useState([]); // Store all variables from all factors
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

        // Fetch current driver data, factor stats, and all breakdowns
        const [driverResponse, ...factorResponses] = await Promise.all([
          api.get(`/api/drivers/${selectedDriverNumber}`),
          api.get('/api/factors/speed/stats'),
          api.get('/api/factors/consistency/stats'),
          api.get('/api/factors/racecraft/stats'),
          api.get('/api/factors/tire_management/stats'),
          api.get(`/api/factors/speed/breakdown/${selectedDriverNumber}`),
          api.get(`/api/factors/consistency/breakdown/${selectedDriverNumber}`),
          api.get(`/api/factors/racecraft/breakdown/${selectedDriverNumber}`),
          api.get(`/api/factors/tire_management/breakdown/${selectedDriverNumber}`)
        ]);

        setDriverData(driverResponse.data);

        // Store factor stats for radar chart
        setFactorStats({
          speed: factorResponses[0].data,
          consistency: factorResponses[1].data,
          racecraft: factorResponses[2].data,
          tire_management: factorResponses[3].data
        });

        // Collect all variables from all factor breakdowns
        const variables = [];
        const breakdowns = [
          factorResponses[4].data,
          factorResponses[5].data,
          factorResponses[6].data,
          factorResponses[7].data
        ];
        breakdowns.forEach(breakdown => {
          if (breakdown.variables) {
            breakdown.variables.forEach(v => {
              variables.push({
                name: v.display_name,
                percentile: v.percentile,
                factor: breakdown.factor_name
              });
            });
          }
        });
        // Sort by percentile descending to get top variables
        variables.sort((a, b) => b.percentile - a.percentile);
        setAllVariables(variables);
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

      {/* AI-Generated Driver Overview - Scouting Report Style */}
      {driverData && (
        <div className="driver-scouting-report">
          <div className="scouting-headline">
            {(() => {
              const factors = [
                { name: 'Speed', adjective: 'fast', score: driverData.speed?.score || 0, max: factorStats.speed?.max || 100 },
                { name: 'Consistency', adjective: 'consistent', score: driverData.consistency?.score || 0, max: factorStats.consistency?.max || 100 },
                { name: 'Racecraft', adjective: 'tactical', score: driverData.racecraft?.score || 0, max: factorStats.racecraft?.max || 100 },
                { name: 'Tire Management', adjective: 'tire-savvy', score: driverData.tire_management?.score || 0, max: factorStats.tire_management?.max || 100 }
              ];
              const sorted = [...factors].sort((a, b) => (b.score / b.max) - (a.score / a.max));
              const top = sorted[0];
              const second = sorted[1];
              const weakest = sorted[3];

              return (
                <>
                  <span className="headline-emphasis">{top.adjective.charAt(0).toUpperCase() + top.adjective.slice(1)}, {second.adjective} driver</span>
                  <span className="headline-detail"> with strong {top.name.toLowerCase()} fundamentals and room to grow in {weakest.name.toLowerCase()}.</span>
                </>
              );
            })()}
          </div>

          <div className="skill-badges-row">
            {allVariables.slice(0, 3).map((variable, idx) => (
              <div key={variable.name} className="skill-badge">
                <div className="badge-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#EB0A1E" strokeWidth="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                </div>
                <span className="badge-label">{variable.name}</span>
                <span className="badge-percentile">{Math.round(variable.percentile)}th</span>
              </div>
            ))}
          </div>

          <div className="scouting-summary">
            <h3>Performance Summary</h3>
            <p>
              {driverData.stats?.best_finish ? (
                <>
                  Season best of <strong>P{driverData.stats.best_finish}</strong> with <strong>P{driverData.stats.average_finish?.toFixed(1)}</strong> average finish.
                </>
              ) : (
                <>Overall field ranking: <strong>#{driverData.overall_rank || 'N/A'}</strong>.</>
              )}
              {' '}
              {(() => {
                const factors = [
                  { name: 'Tire Management', score: driverData.tire_management?.score || 0, max: factorStats.tire_management?.max || 100 },
                  { name: 'Consistency', score: driverData.consistency?.score || 0, max: factorStats.consistency?.max || 100 },
                  { name: 'Racecraft', score: driverData.racecraft?.score || 0, max: factorStats.racecraft?.max || 100 },
                  { name: 'Raw Speed', score: driverData.speed?.score || 0, max: factorStats.speed?.max || 100 }
                ];
                const sorted = [...factors].sort((a, b) => (a.score / a.max) - (b.score / b.max));
                const weakest = sorted[0];
                const gap = Math.round(weakest.max - weakest.score);
                return (
                  <>
                    Primary development focus: <strong>{weakest.name}</strong> ({gap} point gap to leader).
                    Targeted improvement here will unlock significant performance gains.
                  </>
                );
              })()}
            </p>
          </div>
        </div>
      )}

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
                stroke="#EB0A1E"
                fill="#EB0A1E"
                fillOpacity={0.4}
                strokeWidth={4}
              />
            </RadarChart>
          </ResponsiveContainer>
          <div className="radar-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ background: '#EB0A1E' }}></div>
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
          <div className="factor-cards-grid-new">
          {/* Consistency Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Consistency' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Consistency')}
          >
            <button
              className="card-expand-btn"
              title="Click to see detailed breakdown and comparison"
              aria-label="Expand Consistency details"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
            <div className="factor-header-stacked">
              <h3 className="factor-name-large">Consistency</h3>
              <div className="factor-score-large">{Math.round(driverData.consistency?.score || 0)}</div>
            </div>
            <div className="score-bar-container">
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{ width: `${((driverData.consistency?.score || 0) / (factorStats.consistency?.max || 100)) * 100}%` }}
                ></div>
              </div>
              <div className="bar-labels">
                <span>0</span>
                <span>{factorStats.consistency?.max?.toFixed(0) || 100}</span>
              </div>
            </div>
          </div>

          {/* Racecraft Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Racecraft' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Racecraft')}
          >
            <button
              className="card-expand-btn"
              title="Click to see detailed breakdown and comparison"
              aria-label="Expand Racecraft details"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
            <div className="factor-header-stacked">
              <h3 className="factor-name-large">Racecraft</h3>
              <div className="factor-score-large">{Math.round(driverData.racecraft?.score || 0)}</div>
            </div>
            <div className="score-bar-container">
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{ width: `${((driverData.racecraft?.score || 0) / (factorStats.racecraft?.max || 100)) * 100}%` }}
                ></div>
              </div>
              <div className="bar-labels">
                <span>0</span>
                <span>{factorStats.racecraft?.max?.toFixed(0) || 100}</span>
              </div>
            </div>
          </div>

          {/* Raw Speed Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Raw Speed' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Raw Speed')}
          >
            <button
              className="card-expand-btn"
              title="Click to see detailed breakdown and comparison"
              aria-label="Expand Raw Speed details"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
            <div className="factor-header-stacked">
              <h3 className="factor-name-large">Raw Speed</h3>
              <div className="factor-score-large">{Math.round(driverData.speed?.score || 0)}</div>
            </div>
            <div className="score-bar-container">
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{ width: `${((driverData.speed?.score || 0) / (factorStats.speed?.max || 100)) * 100}%` }}
                ></div>
              </div>
              <div className="bar-labels">
                <span>0</span>
                <span>{factorStats.speed?.max?.toFixed(0) || 100}</span>
              </div>
            </div>
          </div>

          {/* Tire Management Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Tire Management' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Tire Management')}
          >
            <button
              className="card-expand-btn"
              title="Click to see detailed breakdown and comparison"
              aria-label="Expand Tire Management details"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
            <div className="factor-header-stacked">
              <h3 className="factor-name-large">Tire Management</h3>
              <div className="factor-score-large">{Math.round(driverData.tire_management?.score || 0)}</div>
            </div>
            <div className="score-bar-container">
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{ width: `${((driverData.tire_management?.score || 0) / (factorStats.tire_management?.max || 100)) * 100}%` }}
                ></div>
              </div>
              <div className="bar-labels">
                <span>0</span>
                <span>{factorStats.tire_management?.max?.toFixed(0) || 100}</span>
              </div>
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

      {/* Coach View Section - Diagnostic Analysis */}
      <div className="coach-view-section">
        <div className="coach-view-header">
          <h2>Driver's Coach View</h2>
          <p>Prioritized weaknesses with telemetry-backed evidence and actionable recommendations</p>
        </div>

        <div className="coach-view-grid">
          {/* Skill Gap Prioritizer */}
          <SkillGapPrioritizer
            driverNumber={selectedDriverNumber}
            onGapSelected={(gap) => {
              console.log('Gap selected:', gap);
            }}
          />

          {/* Coach Recommendations */}
          <CoachRecommendations driverNumber={selectedDriverNumber} />
        </div>
      </div>
    </div>
  );
}
