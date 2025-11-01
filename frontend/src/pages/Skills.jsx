/**
 * Skills Page - 4-factor analysis with spider chart
 * NASCAR aesthetic matching Overview and RaceLog pages
 * Displays driver performance across 4 key factors
 */

import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import api from '../services/api';
import './Skills.css';

export default function Skills() {
  const [driverNumber, setDriverNumber] = useState(13);
  const [driverData, setDriverData] = useState(null);
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
        const response = await api.get(`/api/drivers/${driverNumber}`);
        setDriverData(response.data);
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

  // Prepare radar chart data
  const radarData = [
    {
      factor: 'Consistency',
      value: driverData.consistency?.percentile || 0,
      fullMark: 100
    },
    {
      factor: 'Racecraft',
      value: driverData.racecraft?.percentile || 0,
      fullMark: 100
    },
    {
      factor: 'Raw Speed',
      value: driverData.speed?.percentile || 0,
      fullMark: 100
    },
    {
      factor: 'Tire Mgmt',
      value: driverData.tire_management?.percentile || 0,
      fullMark: 100
    },
  ];

  return (
    <div className="skills-page">
      {/* Header Section */}
      <div className="skills-header">
        <div className="header-content">
          <div className="driver-number-display">
            <span className="number-large">{driverNumber}</span>
          </div>
          <div className="driver-name-section">
            <h1 className="driver-name">Driver #{driverNumber}</h1>
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

      {/* Navigation Tabs */}
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

      {/* Overall Rating Section */}
      <div className="overall-rating-section">
        <div className="overall-rating-card">
          <h3 className="rating-label">Overall Rating</h3>
          <div className="rating-value">{driverData.overall_score || 0}</div>
          <div className="rating-percentile">Top {100 - (driverData.overall_score || 0)}%</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="skills-content">
        {/* Factor Cards Grid */}
        <div className="factor-cards-grid">
          {/* Consistency Card */}
          <div className="factor-card">
            <div className="factor-header">
              <h3 className="factor-name">Consistency</h3>
              <div className="factor-score">{driverData.consistency?.score || 0}</div>
            </div>
            <div className="factor-percentile">
              {driverData.consistency?.percentile || 0}th Percentile
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
          <div className="factor-card">
            <div className="factor-header">
              <h3 className="factor-name">Racecraft</h3>
              <div className="factor-score">{driverData.racecraft?.score || 0}</div>
            </div>
            <div className="factor-percentile">
              {driverData.racecraft?.percentile || 0}th Percentile
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
          <div className="factor-card">
            <div className="factor-header">
              <h3 className="factor-name">Raw Speed</h3>
              <div className="factor-score">{driverData.speed?.score || 0}</div>
            </div>
            <div className="factor-percentile">
              {driverData.speed?.percentile || 0}th Percentile
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
          <div className="factor-card">
            <div className="factor-header">
              <h3 className="factor-name">Tire Management</h3>
              <div className="factor-score">{driverData.tire_management?.score || 0}</div>
            </div>
            <div className="factor-percentile">
              {driverData.tire_management?.percentile || 0}th Percentile
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

        {/* Radar Chart */}
        <div className="radar-chart-container">
          <h3 className="chart-title">Skills Radar</h3>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid
                stroke="#ddd"
                strokeWidth={2}
              />
              <PolarAngleAxis
                dataKey="factor"
                tick={{ fill: '#000', fontSize: 14, fontWeight: 700 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fill: '#666', fontSize: 12, fontWeight: 600 }}
              />
              <Radar
                name="Skills"
                dataKey="value"
                stroke="#e74c3c"
                fill="#e74c3c"
                fillOpacity={0.4}
                strokeWidth={4}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
