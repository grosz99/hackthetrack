/**
 * Overview Page - Driver season statistics
 * Dark F1-inspired theme with modern visualizations
 * Scout Context: Shows breadcrumb and classification when navigated from scout
 */

import { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate, NavLink } from 'react-router-dom';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
         ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
         Legend, ResponsiveContainer } from 'recharts';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import { useScout } from '../../context/ScoutContext';
import { classifyDriver } from '../../utils/classification';
import ClassificationBadge from '../../components/ClassificationBadge/ClassificationBadge';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import './Overview.css';

export default function Overview() {
  const { selectedDriverNumber, setSelectedDriverNumber, drivers } = useDriver();
  const { driverNumber: routeDriverNumber } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [seasonStats, setSeasonStats] = useState(null);
  const [raceResults, setRaceResults] = useState([]);
  const [driverData, setDriverData] = useState(null);
  const [topDrivers, setTopDrivers] = useState([]);
  const [factorStats, setFactorStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFactorInfo, setShowFactorInfo] = useState(false);
  const [expandedCard, setExpandedCard] = useState(null);

  const toggleCard = (cardName) => {
    setExpandedCard(expandedCard === cardName ? null : cardName);
  };

  // Classification for driver
  const classification = driverData ? classifyDriver(driverData) : null;

  // Sync route params with DriverContext
  useEffect(() => {
    if (routeDriverNumber) {
      const driverNum = Number(routeDriverNumber);
      if (driverNum !== selectedDriverNumber) {
        setSelectedDriverNumber(driverNum);
      }
    }
  }, [routeDriverNumber, selectedDriverNumber, setSelectedDriverNumber]);

  useEffect(() => {
    const fetchDriverData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch season stats, race results, driver factors, all drivers, and factor stats in parallel
        const [statsResponse, resultsResponse, driverResponse, allDriversResponse, ...factorResponses] = await Promise.all([
          api.get(`/api/drivers/${selectedDriverNumber}/stats`),
          api.get(`/api/drivers/${selectedDriverNumber}/results`),
          api.get(`/api/drivers/${selectedDriverNumber}`),
          api.get('/api/drivers'),
          api.get('/api/factors/speed/stats'),
          api.get('/api/factors/consistency/stats'),
          api.get('/api/factors/racecraft/stats'),
          api.get('/api/factors/tire_management/stats')
        ]);

        setSeasonStats(statsResponse.data);
        setRaceResults(resultsResponse.data);
        setDriverData(driverResponse.data);

        // Store factor stats for max reference
        setFactorStats({
          speed: factorResponses[0].data,
          consistency: factorResponses[1].data,
          racecraft: factorResponses[2].data,
          tire_management: factorResponses[3].data
        });

        // Get top 3 drivers by overall score (excluding current driver)
        const sortedDrivers = allDriversResponse.data
          .filter(d => d.driver_number !== selectedDriverNumber)
          .sort((a, b) => b.overall_score - a.overall_score)
          .slice(0, 3);

        setTopDrivers(sortedDrivers);
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
      <div className="driver-overview">
        <div className="loading-container">
          <div className="loading-text">Loading driver stats...</div>
        </div>
      </div>
    );
  }

  if (error || !seasonStats) {
    return (
      <div className="driver-overview">
        <div className="error-container">
          <div className="error-text">{error || 'No data available'}</div>
        </div>
      </div>
    );
  }

  // Calculate average of top 3 drivers for each factor
  const getTopAverage = (factor) => {
    if (topDrivers.length === 0) return 0;
    const sum = topDrivers.reduce((acc, driver) => {
      return acc + (driver[factor]?.percentile || 0);
    }, 0);
    return sum / topDrivers.length;
  };

  // Prepare 4-factor radar chart data with top 3 average
  const radarData = driverData ? [
    {
      factor: 'Consistency',
      user: driverData.consistency?.percentile || 0,
      topAvg: getTopAverage('consistency'),
      fullMark: 100
    },
    {
      factor: 'Racecraft',
      user: driverData.racecraft?.percentile || 0,
      topAvg: getTopAverage('racecraft'),
      fullMark: 100
    },
    {
      factor: 'Speed',
      user: driverData.speed?.percentile || 0,
      topAvg: getTopAverage('speed'),
      fullMark: 100
    },
    {
      factor: 'Tire Mgmt',
      user: driverData.tire_management?.percentile || 0,
      topAvg: getTopAverage('tire_management'),
      fullMark: 100
    }
  ] : [];

  // Prepare race performance data for chart
  const racePerformanceData = raceResults.map(result => {
    const delta = (result.start_position - result.finish_position) || 0;
    return {
      race: result.track_name?.substring(0, 8) || `R${result.round}`,
      startPos: result.start_position,
      finishPos: result.finish_position,
      delta: delta,
      deltaPositive: delta > 0 ? delta : 0,
      deltaNegative: delta < 0 ? delta : 0
    };
  });

  return (
    <div className="driver-overview">
      {/* Unified Header with Scout Context */}
      <DashboardHeader driverData={driverData} pageName="Overview" />

      {/* Navigation Tabs - Full Width Below Header */}
      <DashboardTabs />

      {/* Top Section - Compact Tiles + Race Chart */}
      <div className="top-section">
        {/* Compact Performance Tiles - 2x3 Grid */}
        <div className="season-performance-tiles">
          <div className="performance-tile">
            <div className="tile-value">{seasonStats.wins}</div>
            <div className="tile-label">Wins</div>
          </div>

          <div className="performance-tile">
            <div className="tile-value">{seasonStats.podiums}</div>
            <div className="tile-label">Podiums</div>
          </div>

          <div className="performance-tile">
            <div className="tile-value">{seasonStats.pole_positions}</div>
            <div className="tile-label">Poles</div>
          </div>

          <div className="performance-tile">
            <div className="tile-value">{seasonStats.top5}</div>
            <div className="tile-label">Top 5's</div>
          </div>

          <div className="performance-tile">
            <div className="tile-value">{seasonStats.top10}</div>
            <div className="tile-label">Top 10's</div>
          </div>

          <div className="performance-tile">
            <div className="tile-value">{seasonStats.avg_finish.toFixed(1)}</div>
            <div className="tile-label">Avg Finish</div>
          </div>
        </div>

        {/* Race by Race Performance Chart with Expand Button */}
        {racePerformanceData.length > 0 && (
          <div className="race-chart-wrapper">
            <div className="race-performance" style={{ flex: 1 }}>
              <h2>Race by Race Performance</h2>
              <ResponsiveContainer width="100%" height={350}>
                <ComposedChart
                  data={racePerformanceData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 50 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#ddd" />
                  <XAxis
                    dataKey="race"
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    tick={{ fill: '#000', fontSize: 11, fontWeight: 600 }}
                  />
                  <YAxis
                    reversed
                    domain={[1, 20]}
                    label={{ value: 'Position', angle: -90, position: 'insideLeft', fill: '#000', fontWeight: 600 }}
                    tick={{ fill: '#000', fontWeight: 600 }}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', border: '2px solid #EB0A1E', borderRadius: '8px' }}
                    labelStyle={{ color: '#000', fontWeight: 600 }}
                  />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="line"
                  />
                  <Line
                    type="monotone"
                    dataKey="startPos"
                    stroke="#888"
                    strokeWidth={4}
                    name="Starting Position"
                    dot={{ r: 6, fill: '#888', strokeWidth: 3, stroke: '#EB0A1E' }}
                    style={{ filter: 'drop-shadow(0px 0px 2px rgba(231, 76, 60, 0.8))' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="finishPos"
                    stroke="#000"
                    strokeWidth={4}
                    name="Finishing Position"
                    dot={{ r: 6, fill: '#000', strokeWidth: 3, stroke: '#EB0A1E' }}
                    style={{ filter: 'drop-shadow(0px 0px 2px rgba(231, 76, 60, 0.8))' }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* Expand to Race Logs Button */}
            <div className="expand-button-container">
              <NavLink
                to={`/driver/${selectedDriverNumber}/race-log`}
                className="expand-button"
                aria-label="View detailed race logs"
              >
                →
              </NavLink>
              <span className="expand-button-label">
                See Race<br/>Logs
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Section - 4-Factor Performance Analysis */}
      <div className="bottom-section">
        {/* Left side: Spider Chart and Factor Tiles */}
        <div className="race-chart-wrapper">
          {/* 4-Factor Spider Chart */}
          <div className="spider-chart-container">
            <div className="spider-chart-header">
              <h3>Performance Radar - 4 Key Factors</h3>
            </div>
            <button
              className="info-button"
              onClick={() => setShowFactorInfo(true)}
              aria-label="Learn about the 4-factor model"
            >
              ?
            </button>
            <ResponsiveContainer width="100%" height={350}>
            <RadarChart data={radarData} outerRadius="70%">
              <PolarGrid stroke="#ddd" strokeWidth={1} />
              <PolarAngleAxis
                dataKey="factor"
                tick={{ fill: '#000', fontSize: 14, fontWeight: 700 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fill: '#666', fontSize: 11, fontWeight: 600 }}
              />
              {/* Top 3 Average in gray */}
              <Radar
                name="Top 3 Average"
                dataKey="topAvg"
                stroke="#555"
                fill="#555"
                fillOpacity={0.15}
                strokeWidth={2}
              />
              {/* User driver in red - on top */}
              <Radar
                name={`You (#${selectedDriverNumber})`}
                dataKey="user"
                stroke="#EB0A1E"
                fill="#EB0A1E"
                fillOpacity={0.3}
                strokeWidth={3}
              />
            </RadarChart>
          </ResponsiveContainer>

          {/* Legend */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '24px',
            marginTop: '12px',
            fontSize: '13px',
            fontWeight: 600
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{
                width: '24px',
                height: '3px',
                background: '#EB0A1E',
                borderRadius: '2px'
              }}></div>
              <span>You (#{selectedDriverNumber})</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{
                width: '24px',
                height: '3px',
                background: '#555',
                borderRadius: '2px'
              }}></div>
              <span>Top 3 Average</span>
            </div>
          </div>
        </div>

        {/* Skill Development Button */}
        <div className="expand-button-container">
          <NavLink
            to={`/driver/${selectedDriverNumber}/skills`}
            className="expand-button"
            aria-label="View skill development"
          >
            →
          </NavLink>
          <span className="expand-button-label">
            Skill<br/>Development
          </span>
        </div>

        {/* 4 Factor Breakdown Tiles */}
        <div className="factor-tiles-grid">
          {/* Consistency Card */}
          <div className="factor-card">
            <div className="card-expand-container">
              <button
                onClick={() => toggleCard('consistency')}
                className="card-expand-btn"
                title="Click to see what makes up this metric"
                aria-label="Toggle Consistency description"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
              <span className="expand-hint">Click for details</span>
            </div>
            <div className="factor-card-header-stacked">
              <h4 className="factor-card-title-large">Consistency</h4>
              <div className="factor-card-score-large">
                {Math.round(driverData?.consistency?.score || 0)}
              </div>
            </div>
            <div className="factor-card-bar-container">
              <div className="factor-card-bar" style={{
                width: `${((driverData?.consistency?.score || 0) / (factorStats.consistency?.max || 100)) * 100}%`
              }}></div>
            </div>
            <div className="factor-card-bar-labels">
              <span>0</span>
              <span>{factorStats.consistency?.max?.toFixed(0) || 100}</span>
            </div>
            {expandedCard === 'consistency' && (
              <p className="factor-card-description">Measures ability to maintain steady lap times and avoid performance variability throughout a race stint.</p>
            )}
          </div>

          {/* Racecraft Card */}
          <div className="factor-card">
            <div className="card-expand-container">
              <button
                onClick={() => toggleCard('racecraft')}
                className="card-expand-btn"
                title="Click to see what makes up this metric"
                aria-label="Toggle Racecraft description"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
              <span className="expand-hint">Click for details</span>
            </div>
            <div className="factor-card-header-stacked">
              <h4 className="factor-card-title-large">Racecraft</h4>
              <div className="factor-card-score-large">
                {Math.round(driverData?.racecraft?.score || 0)}
              </div>
            </div>
            <div className="factor-card-bar-container">
              <div className="factor-card-bar" style={{
                width: `${((driverData?.racecraft?.score || 0) / (factorStats.racecraft?.max || 100)) * 100}%`
              }}></div>
            </div>
            <div className="factor-card-bar-labels">
              <span>0</span>
              <span>{factorStats.racecraft?.max?.toFixed(0) || 100}</span>
            </div>
            {expandedCard === 'racecraft' && (
              <p className="factor-card-description">Evaluates wheel-to-wheel racing skills including overtaking ability, defensive driving, and position management.</p>
            )}
          </div>

          {/* Speed Card */}
          <div className="factor-card">
            <div className="card-expand-container">
              <button
                onClick={() => toggleCard('speed')}
                className="card-expand-btn"
                title="Click to see what makes up this metric"
                aria-label="Toggle Raw Speed description"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
              <span className="expand-hint">Click for details</span>
            </div>
            <div className="factor-card-header-stacked">
              <h4 className="factor-card-title-large">Raw Speed</h4>
              <div className="factor-card-score-large">
                {Math.round(driverData?.speed?.score || 0)}
              </div>
            </div>
            <div className="factor-card-bar-container">
              <div className="factor-card-bar" style={{
                width: `${((driverData?.speed?.score || 0) / (factorStats.speed?.max || 100)) * 100}%`
              }}></div>
            </div>
            <div className="factor-card-bar-labels">
              <span>0</span>
              <span>{factorStats.speed?.max?.toFixed(0) || 100}</span>
            </div>
            {expandedCard === 'speed' && (
              <p className="factor-card-description">Measures pure pace including qualifying performance, fastest race laps, and overall lap time potential.</p>
            )}
          </div>

          {/* Tire Management Card */}
          <div className="factor-card">
            <div className="card-expand-container">
              <button
                onClick={() => toggleCard('tire_management')}
                className="card-expand-btn"
                title="Click to see what makes up this metric"
                aria-label="Toggle Tire Management description"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
              <span className="expand-hint">Click for details</span>
            </div>
            <div className="factor-card-header-stacked">
              <h4 className="factor-card-title-large">Tire Management</h4>
              <div className="factor-card-score-large">
                {Math.round(driverData?.tire_management?.score || 0)}
              </div>
            </div>
            <div className="factor-card-bar-container">
              <div className="factor-card-bar" style={{
                width: `${((driverData?.tire_management?.score || 0) / (factorStats.tire_management?.max || 100)) * 100}%`
              }}></div>
            </div>
            <div className="factor-card-bar-labels">
              <span>0</span>
              <span>{factorStats.tire_management?.max?.toFixed(0) || 100}</span>
            </div>
            {expandedCard === 'tire_management' && (
              <p className="factor-card-description">Assesses ability to preserve tire performance over long stints and minimize degradation through smooth inputs.</p>
            )}
          </div>
        </div>
      </div>

      {/* Right side: Driver Development Button */}
      <div className="expand-button-container">
        <NavLink
          to={`/driver/${selectedDriverNumber}/skills`}
          className="expand-button"
          aria-label="Driver development"
        >
          →
        </NavLink>
        <span className="expand-button-label">
          Driver<br/>Development
        </span>
      </div>
    </div>

      {/* 4-Factor Model Info Modal */}
      {showFactorInfo && (
        <div className="modal-overlay" onClick={() => setShowFactorInfo(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Understanding the 4-Factor Performance Model</h2>
              <button
                className="modal-close"
                onClick={() => setShowFactorInfo(false)}
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="factor-info-section">
                <h3>Overview</h3>
                <p>
                  The 4-Factor Performance Model breaks down driver performance into four essential dimensions that together reveal your complete racing profile. While raw speed shows how fast you can go, the other three factors—consistency, racecraft, and tire management—determine whether you can sustain that pace under race conditions and execute when it matters. Analyzing all four factors together identifies your strengths and weaknesses, helping you understand not just how fast you are, but how effective you are at converting that speed into race results.
                </p>
              </div>

              <div className="factor-info-section">
                <h3>The 4 Key Factors</h3>
                <div className="factor-definitions">
                  <div className="factor-definition">
                    <strong className="factor-name">Speed:</strong>
                    <span className="factor-description">
                      Measures your raw pace through lap times and sector performance, showing your pure driving ability when pushing to the limit.
                    </span>
                  </div>
                  <div className="factor-definition">
                    <strong className="factor-name">Consistency:</strong>
                    <span className="factor-description">
                      Quantifies how reliably you can reproduce your best performance lap after lap, with lower variation indicating better control and repeatability.
                    </span>
                  </div>
                  <div className="factor-definition">
                    <strong className="factor-name">Racecraft:</strong>
                    <span className="factor-description">
                      Evaluates your wheel-to-wheel racing skills including overtaking efficiency, defensive positioning, and ability to execute race strategy under pressure.
                    </span>
                  </div>
                  <div className="factor-definition">
                    <strong className="factor-name">Tire Management:</strong>
                    <span className="factor-description">
                      Assesses how effectively you preserve tire performance throughout a stint, balancing pace degradation against competitors to maintain speed over longer runs.
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

