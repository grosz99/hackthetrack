/**
 * Overview Page - Driver season statistics
 * Dark F1-inspired theme with modern visualizations
 */

import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
         ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
         Legend, ResponsiveContainer } from 'recharts';
import api from '../services/api';
import './Overview.css';

export default function Overview() {
  const [driverNumber, setDriverNumber] = useState(13);
  const [seasonStats, setSeasonStats] = useState(null);
  const [raceResults, setRaceResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [drivers] = useState([
    { number: 13, name: 'Driver #13' },
    { number: 7, name: 'Driver #7' },
    { number: 22, name: 'Driver #22' },
    { number: 88, name: 'Driver #88' },
    { number: 45, name: 'Driver #45' },
  ]);

  useEffect(() => {
    const fetchDriverData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch season stats and race results in parallel
        const [statsResponse, resultsResponse] = await Promise.all([
          api.get(`/api/drivers/${driverNumber}/stats`),
          api.get(`/api/drivers/${driverNumber}/results`)
        ]);

        setSeasonStats(statsResponse.data);
        setRaceResults(resultsResponse.data);
      } catch (err) {
        console.error('Error fetching driver data:', err);
        setError('Failed to load driver data');
      } finally {
        setLoading(false);
      }
    };

    fetchDriverData();
  }, [driverNumber]);

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

  // Calculate radar chart data
  const maxRaces = seasonStats.total_races || 1;
  const radarData = [
    { metric: 'Wins', value: (seasonStats.wins / maxRaces) * 100, fullMark: 100 },
    { metric: 'Podiums', value: (seasonStats.podiums / maxRaces) * 100, fullMark: 100 },
    { metric: 'Poles', value: (seasonStats.pole_positions / maxRaces) * 100, fullMark: 100 },
    { metric: 'Top 5s', value: (seasonStats.top5 / maxRaces) * 100, fullMark: 100 },
    { metric: 'Top 10s', value: (seasonStats.top10 / maxRaces) * 100, fullMark: 100 },
  ];

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
      {/* Header Section */}
      <div className="driver-header">
        <div className="header-content">
          <div className="driver-number-display">
            <span className="number-large">{seasonStats.driver_number}</span>
          </div>
          <div className="driver-name-section">
            <h1 className="driver-name">Driver #{seasonStats.driver_number}</h1>
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
              value={driverNumber}
              onChange={(e) => setDriverNumber(Number(e.target.value))}
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

      {/* Navigation Tabs - Full Width Below Header */}
      <div className="nav-tabs-container">
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

      {/* Season Performance Section - 2x3 Tiles + Spider Chart */}
      <div className="season-performance-section">
        {/* 2x3 Performance Tiles */}
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

        {/* Performance Radar Chart with Button */}
        <div style={{ display: 'flex', gap: '20px', alignItems: 'stretch' }}>
          <div className="spider-chart-container" style={{ flex: 1 }}>
            <h3>Performance Radar</h3>
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#ddd" />
                <PolarAngleAxis
                  dataKey="metric"
                  tick={{ fill: '#000', fontSize: 12, fontWeight: 600 }}
                />
                <PolarRadiusAxis
                  angle={90}
                  domain={[0, 100]}
                  tick={{ fill: '#666', fontSize: 10 }}
                />
                <Radar
                  name="Performance"
                  dataKey="value"
                  stroke="#e74c3c"
                  fill="#e74c3c"
                  fillOpacity={0.3}
                  strokeWidth={3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Expand to Skills Button */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
            <NavLink
              to="/skills"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#e74c3c',
                color: '#fff',
                fontSize: '36px',
                fontWeight: 900,
                textDecoration: 'none',
                borderRadius: '50%',
                border: '4px solid #fff',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 16px rgba(231, 76, 60, 0.4)',
                width: '80px',
                height: '80px',
                flexShrink: 0
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = '#c0392b';
                e.currentTarget.style.transform = 'scale(1.1)';
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(231, 76, 60, 0.6)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = '#e74c3c';
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(231, 76, 60, 0.4)';
              }}
            >
              →
            </NavLink>
            <span style={{
              fontSize: '12px',
              fontWeight: 700,
              color: '#fff',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              textAlign: 'center'
            }}>
              See<br/>Skills
            </span>
          </div>
        </div>
      </div>

      {/* Race by Race Performance Chart with Expand Button */}
      {racePerformanceData.length > 0 && (
        <div style={{ display: 'flex', gap: '20px', alignItems: 'stretch', marginTop: '24px' }}>
          <div className="race-performance" style={{ flex: 1, marginTop: 0 }}>
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
                  contentStyle={{ backgroundColor: '#fff', border: '2px solid #e74c3c', borderRadius: '8px' }}
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
                  dot={{ r: 6, fill: '#888', strokeWidth: 3, stroke: '#e74c3c' }}
                  style={{ filter: 'drop-shadow(0px 0px 2px rgba(231, 76, 60, 0.8))' }}
                />
                <Line
                  type="monotone"
                  dataKey="finishPos"
                  stroke="#000"
                  strokeWidth={4}
                  name="Finishing Position"
                  dot={{ r: 6, fill: '#000', strokeWidth: 3, stroke: '#e74c3c' }}
                  style={{ filter: 'drop-shadow(0px 0px 2px rgba(231, 76, 60, 0.8))' }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Expand to Race Logs Button */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
            <NavLink
              to="/race-log"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#e74c3c',
                color: '#fff',
                fontSize: '36px',
                fontWeight: 900,
                textDecoration: 'none',
                borderRadius: '50%',
                border: '4px solid #fff',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 16px rgba(231, 76, 60, 0.4)',
                width: '80px',
                height: '80px',
                flexShrink: 0
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = '#c0392b';
                e.currentTarget.style.transform = 'scale(1.1)';
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(231, 76, 60, 0.6)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = '#e74c3c';
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(231, 76, 60, 0.4)';
              }}
            >
              →
            </NavLink>
            <span style={{
              fontSize: '12px',
              fontWeight: 700,
              color: '#fff',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              textAlign: 'center'
            }}>
              See Race<br/>Logs
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

