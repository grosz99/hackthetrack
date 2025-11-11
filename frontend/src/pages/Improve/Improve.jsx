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

      } catch (err) {
        console.error('Error fetching driver data:', err);
        setError('Failed to load driver data');
      } finally {
        setLoading(false);
      }
    };

    fetchDriverData();
  }, [selectedDriverNumber]);

  // Load coaching when selections change
  useEffect(() => {
    if (selectedDriverNumber && selectedTrack && selectedRace) {
      loadCoaching();
    }
  }, [selectedDriverNumber, selectedTrack, selectedRace]);

  const loadCoaching = async () => {
    try {
      setLoadingCoaching(true);
      setError(null);

      const response = await api.get(
        `/api/drivers/${selectedDriverNumber}/telemetry-coaching`,
        {
          params: {
            track_id: selectedTrack,
            race_num: selectedRace
          }
        }
      );

      setCoachingData(response.data);

    } catch (err) {
      console.error('Error loading coaching:', err);
      setError(err.response?.data?.detail || 'Failed to load coaching data for this track.');
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

          <button
            className="analyze-button"
            onClick={loadCoaching}
            disabled={loadingCoaching}
          >
            {loadingCoaching ? 'Loading...' : 'Analyze Performance'}
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

        {/* Performance Analysis Results */}
        {coachingData && !loadingCoaching && (
          <div className="performance-analysis">

            {/* Team Principal's Note */}
            <div className="team-note">
              <div className="team-note-header">Team Principal's Note</div>
              <div className="team-note-content">
                Focus on <strong>{coachingData.summary.primary_weakness}</strong> - you're {coachingData.summary.corners_need_work}/{coachingData.summary.total_corners} corners off pace at {track?.name}
              </div>
            </div>

            {/* Priority Areas (Red Bars) */}
            <div className="priority-areas-section">
              <h3 className="section-title">⚠️ Priority Areas</h3>

              {coachingData.key_insights.map((insight, idx) => (
                <div key={idx} className="priority-item">
                  <div className="priority-bar">
                    <div
                      className="priority-fill"
                      style={{width: `${Math.min(100, (idx + 1) * 20)}%`}}
                    ></div>
                  </div>
                  <div className="priority-text">{insight}</div>
                </div>
              ))}
            </div>

            {/* Top Strengths (Green Checkmarks) */}
            <div className="top-strengths-section">
              <h3 className="section-title">✓ Top Strengths</h3>

              <div className="strengths-grid">
                {coachingData.detailed_comparisons
                  .filter(c => c.insight.includes('similar to fastest'))
                  .map((corner, idx) => (
                    <div key={idx} className="strength-badge">
                      <span className="strength-corner">Turn {corner.corner_num}</span>
                      <span className="strength-text">Similar to fastest driver ✓</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Factor Breakdown */}
            {coachingData.factor_breakdown && (
              <div className="factor-breakdown-section">
                <h3 className="section-title">Performance Factor Breakdown</h3>
                <div className="factor-grid">
                  {Object.entries(coachingData.factor_breakdown).map(([factor, count]) => (
                    <div key={factor} className="factor-card">
                      <div className="factor-name">{factor}</div>
                      <div className="factor-count">{count} corners</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Corner Analysis */}
            {coachingData.detailed_comparisons && (
              <div className="detailed-analysis-section">
                <h3 className="section-title">Detailed Corner Analysis</h3>

                <div className="corners-list">
                  {coachingData.detailed_comparisons.map((corner, idx) => (
                    <div key={idx} className={`corner-detail ${corner.insight.includes('similar') ? 'corner-good' : 'corner-needs-work'}`}>
                      <div className="corner-header">
                        <span className="corner-number">Turn {corner.corner_num}</span>
                        <span className={`corner-factor ${corner.factor.toLowerCase()}`}>{corner.factor}</span>
                      </div>
                      <div className="corner-insight">{corner.insight}</div>
                      <div className="corner-metrics">
                        <span>Speed Delta: {corner.speed_delta_mph > 0 ? '+' : ''}{corner.speed_delta_mph.toFixed(1)} mph</span>
                        <span>Brake Delta: {corner.brake_delta_m > 0 ? '+' : ''}{corner.brake_delta_m.toFixed(0)}m</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

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
