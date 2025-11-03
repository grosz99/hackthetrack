/**
 * Skills Page - 4-factor analysis with spider chart
 * NASCAR aesthetic matching Overview and RaceLog pages
 * Displays driver performance across 4 key factors
 */

import { useState, useEffect } from 'react';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import './Skills.css';

export default function Skills() {
  const { selectedDriverNumber, drivers } = useDriver();
  const [driverData, setDriverData] = useState(null);
  const [topDrivers, setTopDrivers] = useState([]);
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

        // Fetch current driver data and all drivers to find top 3
        const [driverResponse, allDriversResponse] = await Promise.all([
          api.get(`/api/drivers/${selectedDriverNumber}`),
          api.get('/api/drivers')
        ]);

        setDriverData(driverResponse.data);

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

  // Calculate average of top 3 drivers for each factor
  const getTopAverage = (factor) => {
    if (topDrivers.length === 0) return 0;
    const sum = topDrivers.reduce((acc, driver) => {
      return acc + (driver[factor]?.percentile || 0);
    }, 0);
    return sum / topDrivers.length;
  };

  // Prepare radar chart data with top 3 average comparison
  const radarData = [
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
      factor: 'Raw Speed',
      user: driverData.speed?.percentile || 0,
      topAvg: getTopAverage('speed'),
      fullMark: 100
    },
    {
      factor: 'Tire Mgmt',
      user: driverData.tire_management?.percentile || 0,
      topAvg: getTopAverage('tire_management'),
      fullMark: 100
    },
  ];

  const handleFactorClick = async (factorName) => {
    setSelectedFactor(factorName);
    setLoadingBreakdown(true);

    try {
      // Map display names to API factor names
      const factorMap = {
        'Consistency': 'consistency',
        'Racecraft': 'racecraft',
        'Raw Speed': 'speed',
        'Tire Management': 'tire_management'
      };

      const apiFactorName = factorMap[factorName];

      // Fetch both breakdown and comparison data
      const [breakdownResponse, comparisonResponse] = await Promise.all([
        api.get(`/api/drivers/${selectedDriverNumber}/factors/${apiFactorName}`),
        api.get(`/api/drivers/${selectedDriverNumber}/factors/${apiFactorName}/comparison`)
      ]);

      setFactorBreakdown(breakdownResponse.data);
      setFactorComparison(comparisonResponse.data);
    } catch (err) {
      console.error('Error fetching factor breakdown:', err);
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

      {/* OLD HEADER - Hidden */}
      <div className="skills-header" style={{ display: 'none' }}>
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
              onChange={(e) => setSelectedDriverNumber(Number(e.target.value))}
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

      {/* OLD NAV TABS - Hidden */}
      <div className="nav-tabs-container" style={{ display: 'none' }}>
        <div className="nav-tabs">
          <NavLink
            to="/overview"
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >
            Overview
          </NavLink>
          <NavLink
            to="/race-log"
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >
            Race Log
          </NavLink>
          <NavLink
            to="/skills"
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >
            Skills
          </NavLink>
          <NavLink
            to="/improve"
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >
            Improve
          </NavLink>
        </div>
      </div>

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

      {/* Variable Detail View - shown when factor is clicked */}
      {selectedFactor && (
        <div className="variable-detail-section">
          <div className="variable-detail-header">
            <h2>{selectedFactor} Breakdown</h2>
            <button className="close-button" onClick={() => setSelectedFactor(null)}>✕</button>
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
              <p>Failed to load breakdown data</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
