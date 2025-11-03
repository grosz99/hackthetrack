/**
 * Overview Page - Driver season statistics
 * Dark F1-inspired theme with modern visualizations
 * Scout Context: Shows breadcrumb and classification when navigated from scout
 */

import { useState, useEffect } from 'react';
import { NavLink, useParams, useLocation, useNavigate } from 'react-router-dom';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
         ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
         Legend, ResponsiveContainer } from 'recharts';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import { useScout } from '../../context/ScoutContext';
import { classifyDriver } from '../../utils/classification';
import ClassificationBadge from '../../components/ClassificationBadge/ClassificationBadge';
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Detect scout context
  const isFromScout = location.pathname.startsWith('/scout/driver/');
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

        // Fetch season stats, race results, driver factors, and all drivers in parallel
        const [statsResponse, resultsResponse, driverResponse, allDriversResponse] = await Promise.all([
          api.get(`/api/drivers/${selectedDriverNumber}/stats`),
          api.get(`/api/drivers/${selectedDriverNumber}/results`),
          api.get(`/api/drivers/${selectedDriverNumber}`),
          api.get('/api/drivers')
        ]);

        setSeasonStats(statsResponse.data);
        setRaceResults(resultsResponse.data);
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
      {/* Scout Breadcrumb - Only show when navigated from scout */}
      {isFromScout && (
        <div style={{
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px'
        }}>
          <button
            onClick={() => navigate('/scout')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              background: '#e74c3c',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = '#c0392b';
              e.currentTarget.style.transform = 'translateX(-4px)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = '#e74c3c';
              e.currentTarget.style.transform = 'translateX(0)';
            }}
          >
            <span style={{ fontSize: '20px' }}>←</span>
            <span>Back to Scout Portal</span>
          </button>
          <div style={{
            fontSize: '14px',
            fontWeight: 600,
            color: '#666',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ color: '#e74c3c' }}>Scout Portal</span>
            <span>›</span>
            <span style={{ color: '#fff' }}>Driver #{seasonStats.driver_number}</span>
            <span>›</span>
            <span style={{ color: '#fff' }}>Overview</span>
          </div>
        </div>
      )}

      {/* Header Section */}
      <div className="driver-header">
        <div className="header-content">
          <div className="driver-number-display">
            <span className="number-large">{seasonStats.driver_number}</span>
          </div>
          <div className="driver-name-section">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
              <h1 className="driver-name" style={{ margin: 0 }}>Driver #{seasonStats.driver_number}</h1>
              {isFromScout && classification && (
                <ClassificationBadge classification={classification} size="large" />
              )}
            </div>
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

      {/* Navigation Tabs - Full Width Below Header */}
      <div className="nav-tabs-container">
        <div className="nav-tabs">
          <NavLink
            to={isFromScout ? `/scout/driver/${routeDriverNumber || selectedDriverNumber}/overview` : "/overview"}
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >
            Overview
          </NavLink>
          <NavLink
            to={isFromScout ? `/scout/driver/${routeDriverNumber || selectedDriverNumber}/race-log` : "/race-log"}
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >
            Race Log
          </NavLink>
          <NavLink
            to={isFromScout ? `/scout/driver/${routeDriverNumber || selectedDriverNumber}/skills` : "/skills"}
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >
            Skills
          </NavLink>
          <NavLink
            to={isFromScout ? `/scout/driver/${routeDriverNumber || selectedDriverNumber}/improve` : "/improve"}
            className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}
          >
            Improve
          </NavLink>
        </div>
      </div>

      {/* Top Section - Compact Tiles + Race Chart */}
      <div style={{ display: 'flex', gap: '24px', marginBottom: '48px' }}>
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
          <div style={{ display: 'flex', gap: '20px', alignItems: 'stretch', flex: 1 }}>
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
                to={isFromScout ? `/scout/driver/${selectedDriverNumber}/race-log` : "/race-log"}
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

      {/* Bottom Section - 4-Factor Performance Analysis */}
      <div style={{ display: 'flex', gap: '20px', alignItems: 'stretch' }}>
        {/* 4-Factor Spider Chart */}
        <div className="spider-chart-container" style={{ flex: 1 }}>
          <h3>Performance Radar - 4 Key Factors</h3>
          <ResponsiveContainer width="100%" height={350}>
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
                stroke="#e74c3c"
                fill="#e74c3c"
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
                background: '#e74c3c',
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

        {/* 4 Factor Breakdown Tiles */}
        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', alignContent: 'stretch' }}>
          {/* Consistency Card */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '28px 24px',
            border: '4px solid #e74c3c',
            boxShadow: '0 6px 20px rgba(0,0,0,0.12)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ margin: 0, fontSize: '22px', fontWeight: 700, color: '#000' }}>Consistency</h4>
              <div style={{ fontSize: '36px', fontWeight: 900, color: '#e74c3c', lineHeight: 1 }}>
                {Math.round(driverData?.consistency?.score || 0)}
              </div>
            </div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#666', marginBottom: '16px' }}>
              {(driverData?.consistency?.percentile || 0).toFixed(1)}th Percentile
            </div>
            <div style={{ height: '12px', background: '#eee', borderRadius: '6px', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                background: '#e74c3c',
                width: `${driverData?.consistency?.percentile || 0}%`,
                transition: 'width 0.3s ease'
              }}></div>
            </div>
          </div>

          {/* Racecraft Card */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '28px 24px',
            border: '4px solid #e74c3c',
            boxShadow: '0 6px 20px rgba(0,0,0,0.12)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ margin: 0, fontSize: '22px', fontWeight: 700, color: '#000' }}>Racecraft</h4>
              <div style={{ fontSize: '36px', fontWeight: 900, color: '#e74c3c', lineHeight: 1 }}>
                {Math.round(driverData?.racecraft?.score || 0)}
              </div>
            </div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#666', marginBottom: '16px' }}>
              {(driverData?.racecraft?.percentile || 0).toFixed(1)}th Percentile
            </div>
            <div style={{ height: '12px', background: '#eee', borderRadius: '6px', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                background: '#e74c3c',
                width: `${driverData?.racecraft?.percentile || 0}%`,
                transition: 'width 0.3s ease'
              }}></div>
            </div>
          </div>

          {/* Speed Card */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '28px 24px',
            border: '4px solid #e74c3c',
            boxShadow: '0 6px 20px rgba(0,0,0,0.12)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ margin: 0, fontSize: '22px', fontWeight: 700, color: '#000' }}>Raw Speed</h4>
              <div style={{ fontSize: '36px', fontWeight: 900, color: '#e74c3c', lineHeight: 1 }}>
                {Math.round(driverData?.speed?.score || 0)}
              </div>
            </div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#666', marginBottom: '16px' }}>
              {(driverData?.speed?.percentile || 0).toFixed(1)}th Percentile
            </div>
            <div style={{ height: '12px', background: '#eee', borderRadius: '6px', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                background: '#e74c3c',
                width: `${driverData?.speed?.percentile || 0}%`,
                transition: 'width 0.3s ease'
              }}></div>
            </div>
          </div>

          {/* Tire Management Card */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '28px 24px',
            border: '4px solid #e74c3c',
            boxShadow: '0 6px 20px rgba(0,0,0,0.12)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ margin: 0, fontSize: '22px', fontWeight: 700, color: '#000' }}>Tire Mgmt</h4>
              <div style={{ fontSize: '36px', fontWeight: 900, color: '#e74c3c', lineHeight: 1 }}>
                {Math.round(driverData?.tire_management?.score || 0)}
              </div>
            </div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#666', marginBottom: '16px' }}>
              {(driverData?.tire_management?.percentile || 0).toFixed(1)}th Percentile
            </div>
            <div style={{ height: '12px', background: '#eee', borderRadius: '6px', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                background: '#e74c3c',
                width: `${driverData?.tire_management?.percentile || 0}%`,
                transition: 'width 0.3s ease'
              }}></div>
            </div>
          </div>
        </div>

        {/* Expand to Skills Button */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
          <NavLink
            to={isFromScout ? `/scout/driver/${selectedDriverNumber}/skills` : "/skills"}
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
  );
}

