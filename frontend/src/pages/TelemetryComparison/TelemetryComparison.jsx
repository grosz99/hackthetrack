import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { ChartIcon } from '../../components/icons';
import { compareTelemetry, getDrivers, getTracks } from '../../services/api';
import './TelemetryComparison.css';

function TelemetryComparison() {
  const location = useLocation();

  const [trackId, setTrackId] = useState(location.state?.trackId || 'barber');
  const [driver1, setDriver1] = useState(location.state?.driverNumber || null);
  const [driver2, setDriver2] = useState(null);
  const [raceNum, setRaceNum] = useState(1);

  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch tracks and drivers from API
  const [tracks, setTracks] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [initialLoading, setInitialLoading] = useState(true);

  // Load tracks and drivers on mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [tracksData, driversData] = await Promise.all([
          getTracks(),
          getDrivers()
        ]);
        setTracks(tracksData);
        setDrivers(driversData);
      } catch (err) {
        console.error('Error loading initial data:', err);
        setError('Failed to load tracks and drivers');
      } finally {
        setInitialLoading(false);
      }
    };
    loadInitialData();
  }, []);

  const availableDrivers = drivers.map(d => d.driver_number).sort((a, b) => a - b);

  useEffect(() => {
    if (driver1 && driver2 && trackId) {
      loadComparison();
    }
  }, [driver1, driver2, trackId, raceNum]);

  const loadComparison = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await compareTelemetry(trackId, driver1, driver2, raceNum);
      setComparisonData(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  // Prepare lap time chart data
  const lapTimeChartData = comparisonData ? comparisonData.driver_1_laps.map((lap, idx) => {
    const driver2Lap = comparisonData.driver_2_laps[idx];
    return {
      lap: lap.lap_number,
      driver1: lap.lap_time,
      driver2: driver2Lap?.lap_time || null,
    };
  }) : [];

  // Prepare sector delta chart data
  const sectorDeltaData = comparisonData ? [
    {
      sector: 'Sector 1',
      delta: comparisonData.sector_deltas.sector_1,
    },
    {
      sector: 'Sector 2',
      delta: comparisonData.sector_deltas.sector_2,
    },
    {
      sector: 'Sector 3',
      delta: comparisonData.sector_deltas.sector_3,
    },
  ] : [];

  const selectedTrack = tracks.find(t => t.track_id === trackId);

  // Show loading state while fetching initial data
  if (initialLoading) {
    return (
      <div className="telemetry-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="telemetry-container">
      <div className="telemetry-header">
        <h1>Telemetry Comparison</h1>
        <p className="subtitle">Compare lap-by-lap performance to find competitive advantages</p>
      </div>

      {/* Selection Controls */}
      <div className="controls-panel">
        <div className="control-group">
          <label>Track</label>
          <select
            value={trackId}
            onChange={(e) => setTrackId(e.target.value)}
            className="select-input"
          >
            {tracks.map((track) => (
              <option key={track.track_id} value={track.track_id}>
                {track.name}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Race</label>
          <select
            value={raceNum}
            onChange={(e) => setRaceNum(parseInt(e.target.value))}
            className="select-input"
          >
            <option value={1}>Race 1</option>
            <option value={2}>Race 2</option>
          </select>
        </div>

        <div className="control-group">
          <label>Your Driver</label>
          <select
            value={driver1 || ''}
            onChange={(e) => setDriver1(parseInt(e.target.value))}
            className="select-input"
          >
            <option value="">Select Driver</option>
            {availableDrivers.map((num) => (
              <option key={num} value={num}>
                Driver #{num}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Compare Against</label>
          <select
            value={driver2 || ''}
            onChange={(e) => setDriver2(parseInt(e.target.value))}
            className="select-input"
          >
            <option value="">Select Driver</option>
            {availableDrivers.filter(n => n !== driver1).map((num) => (
              <option key={num} value={num}>
                Driver #{num}
              </option>
            ))}
          </select>
        </div>

        <button
          className="compare-button"
          onClick={loadComparison}
          disabled={!driver1 || !driver2 || loading}
        >
          {loading ? 'Loading...' : 'Compare'}
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
          <p className="error-help">
            Make sure the backend API is running and the selected drivers have data for this track.
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading telemetry data...</p>
        </div>
      )}

      {/* Comparison Results */}
      {comparisonData && !loading && (
        <div className="comparison-results">
          {/* Summary Cards */}
          <div className="summary-cards">
            <div className="summary-card">
              <div className="card-label">Total Delta</div>
              <div className={`card-value ${comparisonData.sector_deltas.total >= 0 ? 'negative' : 'positive'}`}>
                {comparisonData.sector_deltas.total >= 0 ? '+' : ''}
                {comparisonData.sector_deltas.total.toFixed(3)}s
              </div>
              <div className="card-description">
                {comparisonData.sector_deltas.total >= 0
                  ? `Driver #${driver2} is faster`
                  : `Driver #${driver1} is faster`}
              </div>
            </div>

            <div className="summary-card">
              <div className="card-label">Biggest Gain</div>
              <div className="card-value positive">
                {Math.max(...Object.values(comparisonData.sector_deltas).filter(v => v < 0).map(Math.abs)).toFixed(3)}s
              </div>
              <div className="card-description">Sector with best advantage</div>
            </div>

            <div className="summary-card">
              <div className="card-label">Biggest Loss</div>
              <div className="card-value negative">
                +{Math.max(...Object.values(comparisonData.sector_deltas).filter(v => v > 0)).toFixed(3)}s
              </div>
              <div className="card-description">Sector to focus improvement</div>
            </div>
          </div>

          {/* Lap Time Comparison Chart */}
          <div className="chart-section">
            <h3>Lap Time Comparison</h3>
            <p className="chart-subtitle">
              Blue = Driver #{driver1} | Red = Driver #{driver2}
            </p>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={lapTimeChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e7" />
                <XAxis
                  dataKey="lap"
                  label={{ value: 'Lap Number', position: 'insideBottom', offset: -5 }}
                  stroke="#86868b"
                />
                <YAxis
                  label={{ value: 'Lap Time (seconds)', angle: -90, position: 'insideLeft' }}
                  stroke="#86868b"
                />
                <Tooltip
                  contentStyle={{
                    background: 'white',
                    border: '1px solid #e5e5e7',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="driver1"
                  stroke="#0071e3"
                  strokeWidth={2}
                  dot={false}
                  name={`Driver #${driver1}`}
                />
                <Line
                  type="monotone"
                  dataKey="driver2"
                  stroke="#EB0A1E"
                  strokeWidth={2}
                  dot={false}
                  name={`Driver #${driver2}`}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Sector Delta Chart */}
          <div className="chart-section">
            <h3>Sector Time Deltas (Best Lap)</h3>
            <p className="chart-subtitle">
              Positive = You're slower | Negative = You're faster
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sectorDeltaData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e7" />
                <XAxis dataKey="sector" stroke="#86868b" />
                <YAxis
                  label={{ value: 'Delta (seconds)', angle: -90, position: 'insideLeft' }}
                  stroke="#86868b"
                />
                <Tooltip
                  contentStyle={{
                    background: 'white',
                    border: '1px solid #e5e5e7',
                    borderRadius: '8px',
                  }}
                  formatter={(value) => `${value >= 0 ? '+' : ''}${value.toFixed(3)}s`}
                />
                <Bar
                  dataKey="delta"
                  fill={(entry) => entry.delta >= 0 ? '#EB0A1E' : '#34C759'}
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Insights */}
          <div className="insights-section">
            <h3>Key Insights</h3>
            <ul className="insights-list">
              {comparisonData.insights.map((insight, idx) => (
                <li key={idx} className="insight-item">
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!comparisonData && !loading && !error && (
        <div className="empty-state">
          <div className="empty-icon"><ChartIcon size="xl" /></div>
          <h3>Compare Driver Telemetry</h3>
          <p>Select two drivers to view detailed performance analysis powered by our validated statistical framework</p>
        </div>
      )}
    </div>
  );
}

export default TelemetryComparison;
