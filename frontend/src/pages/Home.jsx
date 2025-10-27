import { useState, useMemo } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from 'recharts';
import dashboardData from '../data/dashboardData.json';
import './Home.css';
import './Rankings.css';

function Home() {
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [selectedDriver, setSelectedDriver] = useState(null);

  const { drivers, tracks, factor_info, model_stats } = dashboardData;

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
    setSelectedDriver(driver);
    // TODO: Navigate to driver detail page
    alert(`Analyzing Driver #${driver.number} at ${selectedTrack.name}\nPredicted Finish: P${driver.predictedFinish}\nCircuit Fit: ${driver.circuitFitScore}/100`);
  };

  return (
    <div className="home-container">
      {/* Header */}
      <header className="header">
        <div className="gr-logo">GR</div>
        <div className="header-content">
          <h1 className="header-title">Driver Performance Intelligence</h1>
          <p className="header-subtitle">Track-Specific Performance Rankings</p>
        </div>
      </header>

      {/* Track Selection Section */}
      <section className="hero-section">
        <h2 className="hero-title">Select Track</h2>
        <p className="hero-stats">
          Choose a track to see driver rankings and what skills this circuit rewards
        </p>

        {/* Track Grid */}
        <div className="track-grid-large">
          {tracks.map((track) => (
            <div
              key={track.id}
              className={`track-card-large ${selectedTrack?.id === track.id ? 'selected' : ''}`}
              onClick={() => {
                setSelectedTrack(track);
                setSelectedDriver(null); // Reset driver selection
              }}
            >
              <div className="track-map">
                {track.image ? (
                  <img src={track.image} alt={track.name} className="track-image" />
                ) : (
                  <span className="track-placeholder">Track Map</span>
                )}
              </div>
              <div className="track-name">{track.name}</div>
              <div className="track-location">{track.location}</div>
              <div className="track-length">{track.length}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Show track demands and driver rankings only after track is selected */}
      {selectedTrack && (
        <>
          {/* Track Demand Profile */}
          <section className="track-profile-section">
            <h2 className="section-title">{selectedTrack.name} Track Profile</h2>
            <p className="section-subtitle">What skills does this track reward?</p>

            <div className="radar-chart-container">
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#e5e5e7" />
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
                    name="Average Track"
                    dataKey="average"
                    stroke="#d1d1d6"
                    fill="#d1d1d6"
                    fillOpacity={0.3}
                    strokeWidth={2}
                    strokeDasharray="5 5"
                  />
                  <Radar
                    name={selectedTrack.short_name}
                    dataKey="track"
                    stroke="#EB0A1E"
                    fill="#EB0A1E"
                    fillOpacity={0.4}
                    strokeWidth={2}
                  />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="circle"
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Driver Rankings by Circuit Fit */}
          <section className="rankings-section">
            <h2 className="section-title">Driver Rankings at {selectedTrack.name}</h2>
            <p className="section-subtitle">Ranked by circuit fit - click driver to see improvement analysis</p>

            <div className="rankings-table-container">
              <table className="rankings-table">
                <thead>
                  <tr>
                    <th className="col-rank">Rank</th>
                    <th className="col-driver">Driver</th>
                    <th className="col-radar">Skill Radar</th>
                    <th className="col-factor">Consistency</th>
                    <th className="col-factor">Racecraft</th>
                    <th className="col-factor">Raw Speed</th>
                    <th className="col-factor">Tire Mgmt</th>
                    <th className="col-fit">Circuit Fit</th>
                  </tr>
                </thead>
                <tbody>
                  {rankedDrivers.map((driver, index) => (
                    <tr
                      key={driver.number}
                      className={`driver-row ${selectedDriver?.number === driver.number ? 'selected' : ''}`}
                      onClick={() => handleDriverSelect(driver)}
                    >
                      <td className="col-rank">
                        <div className="rank-number">{index + 1}</div>
                      </td>
                      <td className="col-driver">
                        <div className="driver-info-cell">
                          <div className="driver-number">#{driver.number}</div>
                          <span className={`grade-badge ${driver.grade.toLowerCase()}`}>
                            {driver.grade}
                          </span>
                        </div>
                      </td>
                      <td className="col-radar">
                        <div className="radar-mini">
                          <ResponsiveContainer width={110} height={110}>
                            <RadarChart data={driver.radarData}>
                              <PolarGrid stroke="#e5e5e7" strokeWidth={0.5} />
                              <PolarAngleAxis
                                dataKey="skill"
                                tick={false}
                              />
                              <PolarRadiusAxis
                                angle={90}
                                domain={[0, 100]}
                                tick={false}
                                axisLine={false}
                              />
                              <Radar
                                dataKey="trackDemand"
                                stroke="#d1d1d6"
                                fill="#d1d1d6"
                                fillOpacity={0.15}
                                strokeWidth={1}
                                strokeDasharray="2 2"
                              />
                              <Radar
                                dataKey="value"
                                stroke="#EB0A1E"
                                fill="#EB0A1E"
                                fillOpacity={0.25}
                                strokeWidth={2}
                              />
                            </RadarChart>
                          </ResponsiveContainer>
                        </div>
                      </td>
                      <td className="col-factor">
                        {Math.round(driver.factors.consistency.score)}
                      </td>
                      <td className="col-factor">
                        {Math.round(driver.factors.racecraft.score)}
                      </td>
                      <td className="col-factor">
                        {Math.round(driver.factors.raw_speed.score)}
                      </td>
                      <td className="col-factor">
                        {Math.round(driver.factors.tire_mgmt.score)}
                      </td>
                      <td className="col-fit">
                        <div className="fit-cell">{driver.circuitFitScore}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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

export default Home;
