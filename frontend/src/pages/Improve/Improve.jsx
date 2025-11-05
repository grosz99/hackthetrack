/**
 * Improve Page - AI Telemetry Coaching Lab
 *
 * Provides race engineer-style coaching using AI analysis of telemetry data.
 * Compares driver performance vs winner/leader with specific, actionable advice.
 */

import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import ReactMarkdown from 'react-markdown';
import './Improve.css';

// Available tracks with telemetry
const TRACKS = [
  { id: 'barber', name: 'Barber Motorsports Park' },
  { id: 'cota', name: 'Circuit of the Americas' },
  { id: 'roadamerica', name: 'Road America' },
  { id: 'sebring', name: 'Sebring International Raceway' },
  { id: 'sonoma', name: 'Sonoma Raceway' },
  { id: 'vir', name: 'Virginia International Raceway' }
];

export default function Improve() {
  const { selectedDriverNumber, drivers } = useDriver();

  const [driverData, setDriverData] = useState(null);
  const [selectedTrack, setSelectedTrack] = useState('barber');
  const [selectedRace, setSelectedRace] = useState(1);
  const [referenceDriver, setReferenceDriver] = useState(null);
  const [coachingData, setCoachingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingCoaching, setLoadingCoaching] = useState(false);
  const [error, setError] = useState(null);

  // Load driver data
  useEffect(() => {
    const fetchDriverData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await api.get(`/api/drivers/${selectedDriverNumber}`);
        setDriverData(response.data);

        // Auto-select a reference driver (first available driver that's not the user)
        const otherDrivers = drivers.filter(d => d.number !== selectedDriverNumber);
        if (otherDrivers.length > 0 && !referenceDriver) {
          setReferenceDriver(otherDrivers[0].number);
        }

      } catch (err) {
        console.error('Error fetching driver data:', err);
        setError('Failed to load driver data');
      } finally {
        setLoading(false);
      }
    };

    fetchDriverData();
  }, [selectedDriverNumber, drivers, referenceDriver]);

  // Load coaching when selections change
  useEffect(() => {
    if (selectedDriverNumber && referenceDriver && selectedTrack && selectedRace) {
      loadCoaching();
    }
  }, [selectedDriverNumber, referenceDriver, selectedTrack, selectedRace]);

  const loadCoaching = async () => {
    try {
      setLoadingCoaching(true);
      setError(null);

      const response = await api.post('/api/telemetry/coaching', {
        driver_number: selectedDriverNumber,
        reference_driver_number: referenceDriver,
        track_id: selectedTrack,
        race_num: selectedRace
      });

      setCoachingData(response.data);

    } catch (err) {
      console.error('Error loading coaching:', err);
      setError(err.response?.data?.detail || 'Failed to load coaching data. Ensure telemetry data exists for both drivers.');
    } finally {
      setLoadingCoaching(false);
    }
  };

  if (loading) {
    return (
      <div className="improve-page">
        <div className="loading-container">
          <div className="loading-text">Loading...</div>
        </div>
      </div>
    );
  }

  if (!driverData) {
    return (
      <div className="improve-page">
        <div className="error-container">
          <div className="error-text">{error || 'No data available'}</div>
        </div>
      </div>
    );
  }

  const track = TRACKS.find(t => t.id === selectedTrack);
  const refDriver = drivers.find(d => d.number === referenceDriver);

  return (
    <div className="improve-page">
      {/* Unified Header */}
      <DashboardHeader driverData={driverData} pageName="Improve" />

      {/* Unified Navigation Tabs */}
      <DashboardTabs />

      {/* Coaching Content */}
      <div className="coaching-content">

        {/* Selection Controls */}
        <div className="coaching-controls">
          <div className="control-card">
            <label className="control-label">TRACK</label>
            <select
              className="control-select"
              value={selectedTrack}
              onChange={(e) => setSelectedTrack(e.target.value)}
            >
              {TRACKS.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>

          <div className="control-card">
            <label className="control-label">RACE</label>
            <select
              className="control-select"
              value={selectedRace}
              onChange={(e) => setSelectedRace(parseInt(e.target.value))}
            >
              <option value={1}>Race 1</option>
              <option value={2}>Race 2</option>
            </select>
          </div>

          <div className="control-card comparison-card">
            <label className="control-label">COMPARE TO</label>

            {/* Quick Picks - Most Common Comparisons */}
            <div className="comparison-quick-picks">
              <button
                className={`quick-pick-btn ${referenceDriver === drivers.find(d => d.number !== selectedDriverNumber)?.number ? 'active' : ''}`}
                onClick={() => {
                  const nextDriver = drivers.find(d => d.number !== selectedDriverNumber);
                  if (nextDriver) setReferenceDriver(nextDriver.number);
                }}
                title="Compare to race winner or top finisher"
              >
                <span className="quick-pick-label">Winner</span>
              </button>

              <button
                className={`quick-pick-btn ${referenceDriver === drivers[1]?.number ? 'active' : ''}`}
                onClick={() => {
                  if (drivers[1]) setReferenceDriver(drivers[1].number);
                }}
                title="Compare to driver slightly faster than you"
              >
                <span className="quick-pick-label">Next Tier</span>
              </button>
            </div>

            {/* Advanced Selection */}
            <details className="comparison-advanced">
              <summary>Select specific driver</summary>
              <select
                className="control-select"
                value={referenceDriver || ''}
                onChange={(e) => setReferenceDriver(parseInt(e.target.value))}
              >
                <option value="">Select Driver</option>
                {drivers
                  .filter(d => d.number !== selectedDriverNumber)
                  .map(d => (
                    <option key={d.number} value={d.number}>
                      {d.name || `Driver #${d.number}`}
                    </option>
                  ))}
              </select>
            </details>
          </div>

          <button
            className="analyze-button"
            onClick={loadCoaching}
            disabled={loadingCoaching || !referenceDriver}
          >
            {loadingCoaching ? 'Analyzing...' : 'Analyze Telemetry'}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Loading State */}
        {loadingCoaching && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Analyzing telemetry with AI race engineer...</p>
            <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
              This may take 10-15 seconds as Claude analyzes the data
            </p>
          </div>
        )}

        {/* Coaching Results */}
        {coachingData && !loadingCoaching && (
          <div className="coaching-results">

            {/* Hero Metric + Supporting Cards */}
            <div className="metrics-hero-layout">
              {/* Hero Metric - Potential Time Gain */}
              <div className="metric-card hero">
                <div className="metric-label">POTENTIAL TIME GAIN</div>
                <div className="metric-value hero-value">
                  {coachingData.potential_time_gain.toFixed(3)}
                  <span className="metric-unit">s</span>
                </div>
                <div className="metric-subtitle">
                  per lap vs Driver #{coachingData.reference_driver_number}
                </div>
              </div>

              {/* Supporting Metrics */}
              <div className="metrics-secondary">
                <div className="metric-card">
                  <div className="metric-label">LAP DELTA</div>
                  <div className="metric-value">
                    {coachingData.total_time_delta >= 0 ? '+' : ''}
                    {coachingData.total_time_delta.toFixed(3)}s
                  </div>
                  <div className="metric-subtitle">
                    {coachingData.total_time_delta >= 0
                      ? `Driver #${coachingData.reference_driver_number} is faster`
                      : `You are faster`}
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">TRACK</div>
                  <div className="metric-value small">{track?.name || selectedTrack}</div>
                  <div className="metric-subtitle">Race {selectedRace}</div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">FOCUS CORNERS</div>
                  <div className="metric-value small">
                    {coachingData.corner_analysis.filter(c => c.time_loss > 0.05).length}
                  </div>
                  <div className="metric-subtitle">Critical opportunities</div>
                </div>
              </div>
            </div>

            {/* Corner Analysis Table */}
            {coachingData.corner_analysis && coachingData.corner_analysis.length > 0 && (
              <div className="corner-analysis-section">
                <h2 className="section-title">Corner-by-Corner Breakdown</h2>

                <div className="corner-table">
                  <div className="corner-table-header">
                    <div className="corner-col">CORNER</div>
                    <div className="corner-col">YOUR APEX</div>
                    <div className="corner-col">REFERENCE APEX</div>
                    <div className="corner-col">DELTA</div>
                    <div className="corner-col">TIME LOSS</div>
                    <div className="corner-col">FOCUS AREA</div>
                  </div>

                  {coachingData.corner_analysis.map((corner, idx) => (
                    <div
                      key={idx}
                      className={`corner-table-row ${corner.time_loss > 0.05 ? 'loss-row' : ''}`}
                    >
                      <div className="corner-col">
                        <span className="corner-number">{corner.corner_number}</span>
                        <span className="corner-name">{corner.corner_name}</span>
                      </div>
                      <div className="corner-col">{corner.driver_apex_speed.toFixed(1)} km/h</div>
                      <div className="corner-col">{corner.reference_apex_speed.toFixed(1)} km/h</div>
                      <div className={`corner-col ${corner.apex_speed_delta > 0 ? 'negative' : 'positive'}`}>
                        {corner.apex_speed_delta >= 0 ? '+' : ''}
                        {corner.apex_speed_delta.toFixed(1)} km/h
                      </div>
                      <div className="corner-col loss-value">
                        {corner.time_loss.toFixed(3)}s
                      </div>
                      <div className="corner-col focus-area">
                        {corner.focus_area}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Coaching Panel */}
            <div className="ai-coaching-section">
              <div className="coaching-header">
                <div className="coaching-title-row">
                  <h2 className="section-title">Race Engineer Analysis</h2>
                  <div className="coaching-meta">
                    <span className="coaching-badge">AI-Powered Insights</span>
                    <span className="coaching-comparison">
                      #{selectedDriverNumber} vs #{coachingData.reference_driver_number}
                    </span>
                  </div>
                </div>
              </div>

              <div className="coaching-content-card">
                <ReactMarkdown className="coaching-markdown">
                  {coachingData.ai_coaching}
                </ReactMarkdown>
              </div>

              {/* Telemetry Insights */}
              {coachingData.telemetry_insights && (
                <div className="telemetry-insights">
                  <h3 className="insights-title">Telemetry Patterns</h3>
                  <div className="insights-grid">
                    {Object.entries(coachingData.telemetry_insights)
                      .filter(([key]) => !['total_delta', 'potential_gain'].includes(key))
                      .map(([key, value]) => (
                        <div key={key} className="insight-card">
                          <div className="insight-label">
                            {key.replace('_pattern', '').replace('_', ' ').toUpperCase()}
                          </div>
                          <div className="insight-value">{value}</div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>

          </div>
        )}

        {/* Empty State */}
        {!coachingData && !loadingCoaching && !error && (
          <div className="empty-state">
            <h3>Select Track and Reference Driver</h3>
            <p>Choose your configuration above and click "Analyze Telemetry" to get personalized coaching insights</p>
          </div>
        )}

      </div>
    </div>
  );
}
