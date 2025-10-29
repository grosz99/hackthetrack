import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from 'recharts';
import dashboardData from '../data/dashboardData.json';
import './TrackIntelligence.css';
import './Rankings.css';

function TrackIntelligence() {
  const navigate = useNavigate();
  const { drivers, tracks, factor_info, model_stats } = dashboardData;

  // Pre-select Barber track on initial load
  const [selectedTrack, setSelectedTrack] = useState(() => {
    return tracks.find(track => track.id === 'barber') || null;
  });
  const [selectedDriver, setSelectedDriver] = useState(null);

  // Calculate average track demands across all tracks
  const avgDemands = useMemo(() => {
    const totals = tracks.reduce((acc, track) => ({
      consistency: acc.consistency + track.demands.consistency,
      racecraft: acc.racecraft + track.demands.racecraft,
      raw_speed: acc.raw_speed + track.demands.raw_speed,
      tire_mgmt: acc.tire_mgmt + track.demands.tire_mgmt
    }), { consistency: 0, racecraft: 0, raw_speed: 0, tire_mgmt: 0 });

    return {
      consistency: totals.consistency / tracks.length,
      racecraft: totals.racecraft / tracks.length,
      raw_speed: totals.raw_speed / tracks.length,
      tire_mgmt: totals.tire_mgmt / tracks.length
    };
  }, [tracks]);

  // Prepare radar chart data
  const radarData = useMemo(() => {
    if (!selectedTrack) return [];

    // Normalize to 0-1 scale for visualization
    const normalize = (value, avg) => {
      const maxCoefficient = 10; // Approximate max coefficient value
      return (value / maxCoefficient) * 100;
    };

    return [
      {
        skill: 'Consistency',
        track: normalize(selectedTrack.demands.consistency, avgDemands.consistency),
        average: normalize(avgDemands.consistency, avgDemands.consistency),
        fullMark: 100
      },
      {
        skill: 'Racecraft',
        track: normalize(selectedTrack.demands.racecraft, avgDemands.racecraft),
        average: normalize(avgDemands.racecraft, avgDemands.racecraft),
        fullMark: 100
      },
      {
        skill: 'Raw Speed',
        track: normalize(selectedTrack.demands.raw_speed, avgDemands.raw_speed),
        average: normalize(avgDemands.raw_speed, avgDemands.raw_speed),
        fullMark: 100
      },
      {
        skill: 'Tire Mgmt',
        track: normalize(selectedTrack.demands.tire_mgmt, avgDemands.tire_mgmt),
        average: normalize(avgDemands.tire_mgmt, avgDemands.tire_mgmt),
        fullMark: 100
      }
    ];
  }, [selectedTrack, avgDemands]);

  // Calculate circuit fit scores and prepare driver radar data
  const rankedDrivers = useMemo(() => {
    if (!selectedTrack) return [];

    const driversWithFit = drivers.map(driver => {
      // Calculate circuit fit using dot product (negative is better fit)
      const fit =
        (driver.factors.raw_speed.z_score * selectedTrack.demands.raw_speed) +
        (driver.factors.consistency.z_score * selectedTrack.demands.consistency) +
        (driver.factors.racecraft.z_score * selectedTrack.demands.racecraft) +
        (driver.factors.tire_mgmt.z_score * selectedTrack.demands.tire_mgmt);

      // Convert to 0-100 scale (negative fit is better, so invert)
      const fitScore = Math.max(0, Math.min(100, Math.round(50 - (fit * 5))));

      // Create radar data for this driver
      const normalize = (zScore) => {
        // Convert z-score (-3 to +3) to 0-100 scale
        // Negative z-scores are better (above average)
        return Math.max(0, Math.min(100, 50 - (zScore * 15)));
      };

      const driverRadarData = [
        {
          skill: 'Consistency',
          value: normalize(driver.factors.consistency.z_score),
          trackDemand: (selectedTrack.demands.consistency / 10) * 100
        },
        {
          skill: 'Racecraft',
          value: normalize(driver.factors.racecraft.z_score),
          trackDemand: (selectedTrack.demands.racecraft / 10) * 100
        },
        {
          skill: 'Raw Speed',
          value: normalize(driver.factors.raw_speed.z_score),
          trackDemand: (selectedTrack.demands.raw_speed / 10) * 100
        },
        {
          skill: 'Tire Mgmt',
          value: normalize(driver.factors.tire_mgmt.z_score),
          trackDemand: (selectedTrack.demands.tire_mgmt / 10) * 100
        }
      ];

      return {
        ...driver,
        circuitFitScore: fitScore,
        radarData: driverRadarData
      };
    });

    // Sort by circuit fit (higher is better)
    return driversWithFit.sort((a, b) => b.circuitFitScore - a.circuitFitScore);
  }, [selectedTrack, drivers]);

  const handleDriverSelect = (driver) => {
    // Just set the selected driver to show the detail panel
    // Don't navigate - stay on this page
    setSelectedDriver(driver);
  };

  return (
    <div className="home-container">
      {/* Consolidated Hero Header */}
      <section className="hero-header">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="gr-logo-compact">GR</span>
            <span className="hero-label">Driver Intelligence</span>
          </div>
          <h1 className="hero-main-title">Track Performance Rankings</h1>
          <p className="hero-description">
            Advanced analytics revealing which drivers excel at each circuit based on track demands
          </p>

          {/* Compact Track Selector */}
          <div className="track-selector-container">
            <label className="track-selector-label">Select Track:</label>
            <div className="track-pills">
              {tracks.map((track) => (
                <button
                  key={track.id}
                  className={`track-pill ${selectedTrack?.id === track.id ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedTrack(track);
                    setSelectedDriver(null);
                  }}
                >
                  <span className="track-pill-name">{track.short_name}</span>
                  <span className="track-pill-location">{track.location}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Show track analysis only after track is selected */}
      {selectedTrack && (
        <>
          {/* Circuit Demands Section - Full Width Above Rankings */}
          <section className="circuit-demands-section">
            <div className="circuit-demands-container">
              <div className="demands-header">
                <h2 className="demands-title">Circuit Demands: {selectedTrack.name}</h2>
                <p className="demands-subtitle">Performance factors that determine success at this track</p>
              </div>

              <div className="demands-content">
                <div className="radar-chart-wrapper">
                  <ResponsiveContainer width="100%" height={380}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="#e5e5e7" strokeWidth={1} />
                      <PolarAngleAxis
                        dataKey="skill"
                        tick={{ fill: '#1d1d1f', fontSize: 14, fontWeight: 600 }}
                      />
                      <PolarRadiusAxis
                        angle={90}
                        domain={[0, 100]}
                        tick={{ fill: '#86868b', fontSize: 12 }}
                      />
                      <Radar
                        name="Average Track Fit"
                        dataKey="average"
                        stroke="#9e9ea3"
                        fill="#9e9ea3"
                        fillOpacity={0.15}
                        strokeWidth={2}
                        strokeDasharray="5 5"
                      />
                      <Radar
                        name="Podium Finishers"
                        dataKey="track"
                        stroke="#EB0A1E"
                        fill="#EB0A1E"
                        fillOpacity={0.25}
                        strokeWidth={3}
                      />
                      <Legend
                        wrapperStyle={{ paddingTop: '20px' }}
                        iconType="circle"
                        iconSize={12}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>

                <div className="track-insights-panel">
                  <div className="insights-header">
                    <h3 className="insights-title">Track Analysis</h3>
                    <div className="track-meta">
                      <span className="meta-item">{selectedTrack.location}</span>
                      <span className="meta-divider">•</span>
                      <span className="meta-item">{selectedTrack.length}</span>
                    </div>
                  </div>

                  <p className="track-insight-text">
                    {selectedTrack.insight}
                  </p>

                  <div className="legend-explainer">
                    <div className="legend-item">
                      <div className="legend-icon avg"></div>
                      <span className="legend-text"><strong>Average Track Fit:</strong> Baseline performance across all drivers</span>
                    </div>
                    <div className="legend-item">
                      <div className="legend-icon podium"></div>
                      <span className="legend-text"><strong>Podium Finishers:</strong> Skill profile of race winners at this track</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Driver Rankings Section - Two Column Layout Like Above */}
          <section className="rankings-section-wrapper">
            <div className="rankings-two-column">
              {/* Left Column: Rankings Table */}
              <div className="rankings-main">
                <div className="rankings-header">
                <div>
                  <h2 className="rankings-title">Driver Rankings</h2>
                  <p className="rankings-subtitle">
                    Sorted by circuit fit score • Click any row for detailed analysis
                  </p>
                </div>
              </div>

                {/* Grid-Based Table */}
                <div className="rankings-grid-container">
                  {/* Header Row */}
                  <div className="grid-header">
                    <div className="grid-cell header-cell rank-col">#</div>
                    <div className="grid-cell header-cell driver-col">DRIVER</div>
                    <div className="grid-cell header-cell stat-col">
                      <span className="header-with-info">
                        CONSISTENCY
                        <span className="info-icon" data-tooltip={factor_info.consistency.description}>ⓘ</span>
                      </span>
                    </div>
                    <div className="grid-cell header-cell stat-col">
                      <span className="header-with-info">
                        RACECRAFT
                        <span className="info-icon" data-tooltip={factor_info.racecraft.description}>ⓘ</span>
                      </span>
                    </div>
                    <div className="grid-cell header-cell stat-col">
                      <span className="header-with-info">
                        RAW SPEED
                        <span className="info-icon" data-tooltip={factor_info.raw_speed.description}>ⓘ</span>
                      </span>
                    </div>
                    <div className="grid-cell header-cell stat-col">
                      <span className="header-with-info">
                        TIRE MGMT
                        <span className="info-icon" data-tooltip={factor_info.tire_mgmt.description}>ⓘ</span>
                      </span>
                    </div>
                    <div className="grid-cell header-cell fit-col">
                      <span className="header-with-info">
                        CIRCUIT FIT
                        <span className="info-icon" data-tooltip="Calculated by matching driver skill profile to track demands. Higher scores indicate better track-driver fit based on consistency, racecraft, raw speed, and tire management factors.">ⓘ</span>
                      </span>
                    </div>
                  </div>

                  {/* Data Rows */}
                  {rankedDrivers.map((driver, index) => (
                    <div
                      key={driver.number}
                      className={`grid-row ${selectedDriver?.number === driver.number ? 'selected' : ''}`}
                      onClick={() => handleDriverSelect(driver)}
                    >
                      <div className="grid-cell rank-col">
                        <span className="rank-number">{index + 1}</span>
                      </div>
                      <div className="grid-cell driver-col">
                        <span className="driver-number">#{driver.number}</span>
                      </div>
                      <div className="grid-cell stat-col">
                        <span className="stat-value">{driver.factors.consistency.score}</span>
                      </div>
                      <div className="grid-cell stat-col">
                        <span className="stat-value">{driver.factors.racecraft.score}</span>
                      </div>
                      <div className="grid-cell stat-col">
                        <span className="stat-value">{driver.factors.raw_speed.score}</span>
                      </div>
                      <div className="grid-cell stat-col">
                        <span className="stat-value">{driver.factors.tire_mgmt.score}</span>
                      </div>
                      <div className="grid-cell fit-col">
                        <span className="fit-value">{driver.circuitFitScore}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right Column: Driver Detail Panel */}
              {selectedDriver && (
              <aside className="driver-detail-panel">
                <div className="panel-header">
                  <div className="panel-title-section">
                    <h3 className="panel-driver-number">#{selectedDriver.number}</h3>
                    <span className={`panel-grade-badge ${selectedDriver.grade.toLowerCase()}`}>
                      {selectedDriver.grade}
                    </span>
                  </div>
                  <div className="panel-fit-score">
                    <span className="fit-label">Circuit Fit</span>
                    <span className="fit-number">{selectedDriver.circuitFitScore}</span>
                  </div>
                </div>

                <div className="panel-section">
                  <h4 className="section-heading">Profile vs Track Demands</h4>
                  <div className="panel-radar">
                    <ResponsiveContainer width="100%" height={240}>
                      <RadarChart data={selectedDriver.radarData}>
                        <PolarGrid stroke="#e5e5e7" strokeWidth={0.5} />
                        <PolarAngleAxis
                          dataKey="skill"
                          tick={{ fill: '#1d1d1f', fontSize: 11, fontWeight: 600 }}
                        />
                        <PolarRadiusAxis
                          angle={90}
                          domain={[0, 100]}
                          tick={false}
                          axisLine={false}
                        />
                        <Radar
                          name="Track Demand"
                          dataKey="trackDemand"
                          stroke="#d1d1d6"
                          fill="#d1d1d6"
                          fillOpacity={0.15}
                          strokeWidth={1.5}
                          strokeDasharray="3 3"
                        />
                        <Radar
                          name="Driver Profile"
                          dataKey="value"
                          stroke="#EB0A1E"
                          fill="#EB0A1E"
                          fillOpacity={0.3}
                          strokeWidth={2}
                        />
                        <Legend
                          wrapperStyle={{ paddingTop: '12px' }}
                          iconType="circle"
                          iconSize={10}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="panel-section">
                  <h4 className="section-heading">Performance Factors</h4>
                  <div className="factor-list">
                    <div className="factor-item">
                      <div className="factor-header">
                        <span className="factor-name">Raw Speed</span>
                        <span className="factor-importance high">High Impact</span>
                      </div>
                      <div className="factor-bar-container">
                        <div
                          className="factor-bar"
                          style={{ width: `${selectedDriver.factors.raw_speed.score}%` }}
                        ></div>
                        <span className="factor-score-text">{selectedDriver.factors.raw_speed.score}</span>
                      </div>
                    </div>

                    <div className="factor-item">
                      <div className="factor-header">
                        <span className="factor-name">Consistency</span>
                        <span className="factor-importance high">High Impact</span>
                      </div>
                      <div className="factor-bar-container">
                        <div
                          className="factor-bar"
                          style={{ width: `${selectedDriver.factors.consistency.score}%` }}
                        ></div>
                        <span className="factor-score-text">{selectedDriver.factors.consistency.score}</span>
                      </div>
                    </div>

                    <div className="factor-item">
                      <div className="factor-header">
                        <span className="factor-name">Tire Management</span>
                        <span className="factor-importance medium">Medium Impact</span>
                      </div>
                      <div className="factor-bar-container">
                        <div
                          className="factor-bar"
                          style={{ width: `${selectedDriver.factors.tire_mgmt.score}%` }}
                        ></div>
                        <span className="factor-score-text">{selectedDriver.factors.tire_mgmt.score}</span>
                      </div>
                    </div>

                    <div className="factor-item">
                      <div className="factor-header">
                        <span className="factor-name">Racecraft</span>
                        <span className="factor-importance low">Lower Impact</span>
                      </div>
                      <div className="factor-bar-container">
                        <div
                          className="factor-bar"
                          style={{ width: `${selectedDriver.factors.racecraft.score}%` }}
                        ></div>
                        <span className="factor-score-text">{selectedDriver.factors.racecraft.score}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="panel-section">
                  <h4 className="section-heading">Track Performance</h4>
                  <div className="stats-grid">
                    <div className="stat-box">
                      <span className="stat-label">Avg Finish</span>
                      <span className="stat-value">{selectedDriver.avg_finish.toFixed(1)}</span>
                    </div>
                    <div className="stat-box">
                      <span className="stat-label">Races</span>
                      <span className="stat-value">{selectedDriver.races}</span>
                    </div>
                    <div className="stat-box">
                      <span className="stat-label">Percentile</span>
                      <span className="stat-value">{selectedDriver.percentile}th</span>
                    </div>
                  </div>
                </div>
              </aside>
              )}
            </div>
          </section>
        </>
      )}

      {/* Footer */}
      <footer className="footer">
        Model validation: R² = {model_stats.r_squared} | Cross-Val R² = {model_stats.cross_val_r_squared} | MAE = {model_stats.mae} positions | {model_stats.races_analyzed} races analyzed
      </footer>
    </div>
  );
}

export default TrackIntelligence;
