/**
 * Skills Page - 4-factor analysis with spider chart
 * NASCAR aesthetic matching Overview and RaceLog pages
 * Displays driver performance across 4 key factors
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import './Skills.css';

export default function Skills() {
  const navigate = useNavigate();
  const { selectedDriverNumber, drivers } = useDriver();

  // Get current driver name
  const currentDriver = drivers.find(d => d.number === selectedDriverNumber);
  const currentDriverName = currentDriver?.name || `Driver #${selectedDriverNumber}`;

  const [driverData, setDriverData] = useState(null);
  const [factorStats, setFactorStats] = useState({}); // NEW: Store factor stats from efficient endpoint
  const [allVariables, setAllVariables] = useState([]); // Store all variables from all factors
  const [selectedFactor, setSelectedFactor] = useState(null);
  const [factorBreakdown, setFactorBreakdown] = useState(null);
  const [factorComparison, setFactorComparison] = useState(null);
  const [coachingAnalysis, setCoachingAnalysis] = useState(null);
  const [loadingCoaching, setLoadingCoaching] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingBreakdown, setLoadingBreakdown] = useState(false);
  const [error, setError] = useState(null);
  const [showRadarInfo, setShowRadarInfo] = useState(false);

  useEffect(() => {
    const fetchDriverData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Clear factor selection when driver changes
        setSelectedFactor(null);
        setFactorBreakdown(null);
        setFactorComparison(null);
        setCoachingAnalysis(null);

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
    setCoachingAnalysis(null);
    setLoadingCoaching(false);
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

      // Fetch AI coaching analysis asynchronously (don't block the UI)
      setLoadingCoaching(true);
      api.get(`/api/factors/${apiFactorName}/coaching/${selectedDriverNumber}`)
        .then(coachingResponse => {
          setCoachingAnalysis(coachingResponse.data);
          setLoadingCoaching(false);
        })
        .catch(coachingErr => {
          console.error('[Skills] Error loading AI coaching:', coachingErr);
          setLoadingCoaching(false);
        });
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

      {/* AI-Generated Driver Overview - NBA Scouting Report Style */}
      {driverData && (
        <div className="scouting-report-section">
          <h2 className="scouting-report-title">SCOUTING REPORT</h2>

          <p className="scouting-headline-big">
            {(() => {
              const factors = [
                {
                  name: 'speed',
                  adjective: 'fast',
                  score: driverData.speed?.score || 0,
                  max: factorStats.speed?.max || 100,
                  percentile: driverData.speed?.percentile || 0
                },
                {
                  name: 'consistency',
                  adjective: 'consistent',
                  score: driverData.consistency?.score || 0,
                  max: factorStats.consistency?.max || 100,
                  percentile: driverData.consistency?.percentile || 0
                },
                {
                  name: 'racecraft',
                  adjective: 'tactical',
                  score: driverData.racecraft?.score || 0,
                  max: factorStats.racecraft?.max || 100,
                  percentile: driverData.racecraft?.percentile || 0
                },
                {
                  name: 'tire management',
                  adjective: 'tire-savvy',
                  score: driverData.tire_management?.score || 0,
                  max: factorStats.tire_management?.max || 100,
                  percentile: driverData.tire_management?.percentile || 0
                }
              ];
              const sorted = [...factors].sort((a, b) => (b.score / b.max) - (a.score / a.max));
              const top = sorted[0];
              const second = sorted[1];
              const weakest = sorted[3];

              // Generate more personalized description based on driver performance
              const avgPercentile = factors.reduce((sum, f) => sum + f.percentile, 0) / factors.length;

              let description;
              if (avgPercentile >= 75) {
                // Elite driver
                description = `${currentDriverName} is an elite competitor who excels in ${top.name}, ranking in the ${Math.round(top.percentile)}th percentile. Their ${second.adjective} approach complements their natural ${top.adjective} abilities, though ${weakest.name} remains an area for continued development to reach championship-caliber performance.`;
              } else if (avgPercentile >= 50) {
                // Above average driver
                description = `${currentDriverName} shows strong ${top.adjective} capabilities with ${top.name} as their calling card (${Math.round(top.percentile)}th percentile). They demonstrate ${second.adjective} tendencies that make them competitive on race day. Focusing development on ${weakest.name} could unlock the next level of performance.`;
              } else {
                // Developing driver
                description = `${currentDriverName} is a developing talent with clear strengths in ${top.name} (${Math.round(top.percentile)}th percentile). Their ${second.adjective} driving style provides a solid foundation to build upon. Significant gains are possible through targeted work on ${weakest.name} fundamentals.`;
              }

              return (
                <span className="headline-light">{description}</span>
              );
            })()}
          </p>

          <div className="scouting-badges">
            {allVariables.slice(0, 4).map((variable) => (
              <div key={variable.name} className="scouting-badge">
                <div className="scouting-badge-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EB0A1E" strokeWidth="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                </div>
                <span className="scouting-badge-label">{variable.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Content Grid - Radar Left, Factor Cards Right */}
      <div className="skills-content-new">
        {/* Radar Chart on left side */}
        <div className="radar-chart-container-new">
          <div className="chart-header-with-info">
            <h3 className="chart-title">Performance Comparison</h3>
            <button
              className="info-button"
              onClick={() => setShowRadarInfo(true)}
              aria-label="How to interpret this radar chart"
            >
              ?
            </button>
          </div>
          <div className="radar-legend-top">
            <div className="legend-item">
              <div className="legend-color" style={{ background: '#EB0A1E' }}></div>
              <span>{currentDriverName}</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ background: '#555' }}></div>
              <span>Top 3 Average</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={480}>
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
                name={currentDriverName}
                dataKey="user"
                stroke="#EB0A1E"
                fill="#EB0A1E"
                fillOpacity={0.4}
                strokeWidth={4}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Factor Cards Grid - 2x2 on right side */}
        <div className="factor-cards-container">
          {/* Instructional Banner */}
          <div className="factor-instructions-banner">
            <p className="instructions-text">
              <strong>Explore Each Factor:</strong> Click the <span className="plus-icon-inline">+</span> button on any card below to see the detailed variables that make up each factor and get personalized coaching on how this driver can improve.
            </p>
          </div>

          <div className="factor-cards-grid-new">
          {/* Consistency Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Consistency' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Consistency')}
          >
            <button
              className="card-expand-btn"
              title="Click to learn more about this factor"
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
            <p className="factor-description">Measures ability to maintain steady lap times and avoid performance variability throughout a race stint.</p>
          </div>

          {/* Racecraft Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Racecraft' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Racecraft')}
          >
            <button
              className="card-expand-btn"
              title="Click to learn more about this factor"
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
            <p className="factor-description">Evaluates wheel-to-wheel racing skills including overtaking ability, defensive driving, and position management.</p>
          </div>

          {/* Raw Speed Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Raw Speed' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Raw Speed')}
          >
            <button
              className="card-expand-btn"
              title="Click to learn more about this factor"
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
            <p className="factor-description">Measures pure pace including qualifying performance, fastest race laps, and overall lap time potential.</p>
          </div>

          {/* Tire Management Card */}
          <div
            className={`factor-card-large ${selectedFactor === 'Tire Management' ? 'selected' : ''}`}
            onClick={() => handleFactorClick('Tire Management')}
          >
            <button
              className="card-expand-btn"
              title="Click to learn more about this factor"
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
            <p className="factor-description">Assesses ability to preserve tire performance over long stints and minimize degradation through smooth inputs.</p>
          </div>
          </div>
        </div>
      </div>

      {/* Variable Detail View - shown when factor is clicked */}
      {selectedFactor && (
        <div className="breakdown-layout">
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
                {factorBreakdown.variables.map((variable, index) => {
                  // Calculate ranking from percentile (assuming ~34 drivers)
                  const totalDrivers = 34;
                  const rank = Math.round(totalDrivers * (1 - variable.percentile / 100)) + 1;
                  const clampedRank = Math.min(Math.max(rank, 1), totalDrivers);

                  return (
                    <div key={index} className="variable-card">
                      <div className="variable-header">
                        <h4>{variable.display_name}</h4>
                        <span className="variable-rank">{clampedRank}{clampedRank === 1 ? 'st' : clampedRank === 2 ? 'nd' : clampedRank === 3 ? 'rd' : 'th'} of {totalDrivers}</span>
                      </div>
                      <p className="variable-description">{variable.description}</p>

                      {/* Percentile Distribution Chart */}
                      <div className="percentile-distribution">
                        <div className="distribution-track">
                          {/* Quartile zones background */}
                          <div className="quartile-zones">
                            <div className="quartile-zone q1-zone"></div>
                            <div className="quartile-zone q2-zone"></div>
                            <div className="quartile-zone q3-zone"></div>
                            <div className="quartile-zone q4-zone"></div>
                          </div>

                          {/* Quartile markers */}
                          <div className="quartile-marker" style={{ left: '25%' }}>
                            <div className="marker-line"></div>
                          </div>
                          <div className="quartile-marker" style={{ left: '50%' }}>
                            <div className="marker-line median"></div>
                          </div>
                          <div className="quartile-marker" style={{ left: '75%' }}>
                            <div className="marker-line"></div>
                          </div>

                          {/* Driver position dot */}
                          <div
                            className="driver-position-dot"
                            style={{ left: `${variable.percentile}%` }}
                            data-percentile={`${variable.percentile.toFixed(0)}th percentile`}
                          >
                            <div className="dot-pulse"></div>
                          </div>
                        </div>

                        {/* Scale labels */}
                        <div className="distribution-labels">
                          <span className="label-left">Needs Work</span>
                          <span className="label-right">Elite</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Scout's Assessment Section */}
              <div className="scouts-assessment">
                <div className="scouts-assessment-header">
                  <h3 className="scouts-assessment-title">Scout's Assessment</h3>
                </div>
                {loadingCoaching ? (
                  <div className="assessment-loading">
                    <div className="assessment-spinner"></div>
                    <span className="assessment-loading-text">Generating scouting report...</span>
                  </div>
                ) : coachingAnalysis ? (
                  <>
                    <div className="assessment-stats">
                      <div className="stat-pill">
                        <span className="stat-pill-value">#{coachingAnalysis.factor_rank}</span>
                        <span className="stat-pill-label">Overall Rank</span>
                      </div>
                      <div className="stat-pill">
                        <span className="stat-pill-value">{coachingAnalysis.factor_percentile.toFixed(0)}th</span>
                        <span className="stat-pill-label">Percentile</span>
                      </div>
                      <div className="stat-pill">
                        <span className="stat-pill-value">{coachingAnalysis.total_drivers}</span>
                        <span className="stat-pill-label">Drivers</span>
                      </div>
                    </div>
                    <div className="assessment-body">
                      <p className="assessment-text">{coachingAnalysis.coaching_analysis}</p>
                    </div>
                  </>
                ) : (
                  <div className="assessment-body">
                    <p className="assessment-text" style={{ color: '#666', textAlign: 'center' }}>
                      Scouting assessment unavailable. View the metrics breakdown above for detailed performance data.
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="error-breakdown">
              <p>Unable to load factor breakdown. Please try again.</p>
            </div>
          )}
        </div>

        {/* Sticky Action Button - Driver Development */}
        <div className="skills-action-button-container">
          <button
            className="skills-circular-action-btn"
            onClick={() => navigate(`/driver/${selectedDriverNumber}/improve`)}
            aria-label="View driver development resources"
          >
            →
          </button>
          <span className="skills-action-button-label">
            Driver<br/>Development
          </span>
        </div>
        </div>
      )}

      {/* Radar Chart Interpretation Modal */}
      {showRadarInfo && (
        <div className="modal-overlay" onClick={() => setShowRadarInfo(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>How to Interpret the Performance Radar Chart</h2>
              <button
                className="modal-close"
                onClick={() => setShowRadarInfo(false)}
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="factor-info-section">
                <h3>For Coaches: Reading the Radar</h3>
                <p>
                  The Performance Comparison radar chart visualizes your driver's percentile rankings across all four performance factors compared to the top 3 drivers in the field. This visualization makes it immediately clear where your driver excels and where development is needed.
                </p>
              </div>

              <div className="factor-info-section">
                <h3>What the Chart Shows</h3>
                <ul className="info-list">
                  <li><strong>Red Area ({currentDriverName}):</strong> Your driver's percentile performance in each factor. Larger area means stronger all-around performance.</li>
                  <li><strong>Gray Area (Top 3 Average):</strong> The average performance of the top 3 drivers. This represents elite-level benchmarks to target.</li>
                  <li><strong>Each Axis (0-100):</strong> Percentile ranking, where 100 = best in field and 0 = lowest in field.</li>
                </ul>
              </div>

              <div className="factor-info-section">
                <h3>Coaching Interpretation Guide</h3>
                <ul className="info-list">
                  <li><strong>Balanced Shape:</strong> A relatively even diamond indicates well-rounded development. Focus on incremental gains across all areas.</li>
                  <li><strong>Spiky Shape:</strong> Significant variance between factors reveals clear strengths and weaknesses. Prioritize addressing the weakest factor while maintaining strengths.</li>
                  <li><strong>Red Exceeds Gray:</strong> When your driver's area extends beyond the gray benchmark in a factor, they are performing at or above elite level in that dimension.</li>
                  <li><strong>Gray Exceeds Red:</strong> Gaps between the gray and red areas highlight development opportunities. Larger gaps indicate higher-priority training focus areas.</li>
                  <li><strong>Overall Size:</strong> A larger red area relative to gray suggests your driver is competitive with top performers. A smaller area indicates room for substantial overall improvement.</li>
                </ul>
              </div>

              <div className="factor-info-section">
                <h3>Development Strategy</h3>
                <p>
                  Use this chart to guide training priorities. While it's tempting to focus solely on weaknesses, remember that <strong>elite drivers often win by maximizing their strengths</strong> while bringing weaknesses to "good enough" levels. For developing drivers, addressing major deficiencies first creates the fastest path to competitive performance.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
