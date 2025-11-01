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
  const [driverNumber] = useState(13);
  const [seasonStats, setSeasonStats] = useState(null);
  const [raceResults, setRaceResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
  const racePerformanceData = raceResults.map(result => ({
    race: result.track_name?.substring(0, 8) || `R${result.round}`,
    startPos: result.start_position,
    finishPos: result.finish_position,
    delta: result.positions_gained || 0
  }));

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
            <div className="season-subtitle">Indycar Pro Series</div>
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

        {/* Performance Radar Chart */}
        <div className="spider-chart-container">
          <h3>Performance Radar</h3>
          <ResponsiveContainer width="100%" height={400}>
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
      </div>

      {/* Race by Race Performance Chart */}
      {racePerformanceData.length > 0 && (
        <div className="race-performance">
          <h2>Race by Race Performance</h2>
          <ResponsiveContainer width="100%" height={400}>
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
                yAxisId="position"
                reversed
                domain={[1, 20]}
                label={{ value: 'Position', angle: -90, position: 'insideLeft', fill: '#000', fontWeight: 600 }}
                tick={{ fill: '#000', fontWeight: 600 }}
              />
              <YAxis
                yAxisId="delta"
                orientation="right"
                domain={[-10, 10]}
                label={{ value: 'Position Change', angle: 90, position: 'insideRight', fill: '#000', fontWeight: 600 }}
                tick={{ fill: '#000', fontWeight: 600 }}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '2px solid #e74c3c', borderRadius: '8px' }}
                labelStyle={{ color: '#000', fontWeight: 600 }}
                formatter={(value, name) => {
                  if (name === 'Position Change') {
                    return value > 0 ? `+${value}` : value;
                  }
                  return value;
                }}
              />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              <Line
                yAxisId="position"
                type="monotone"
                dataKey="startPos"
                stroke="#e74c3c"
                strokeWidth={3}
                name="Starting Position"
                dot={{ r: 5, fill: '#e74c3c', strokeWidth: 2, stroke: '#fff' }}
              />
              <Line
                yAxisId="position"
                type="monotone"
                dataKey="finishPos"
                stroke="#2ecc71"
                strokeWidth={3}
                name="Finishing Position"
                dot={{ r: 5, fill: '#2ecc71', strokeWidth: 2, stroke: '#fff' }}
              />
              <Bar
                yAxisId="delta"
                dataKey="delta"
                fill="#e74c3c"
                name="Position Change"
                opacity={0.4}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

