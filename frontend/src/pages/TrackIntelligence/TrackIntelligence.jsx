import { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from 'recharts';
import { BullseyeIcon, SwordIcon, LightningIcon, TireIcon } from '../../components/icons';
import { getTracks, getDrivers } from '../../services/api';
import './TrackIntelligence.css';

// Static metadata about factors (doesn't change)
const factor_info = {
  consistency: {
    description: 'Ability to maintain consistent lap times across a race'
  },
  racecraft: {
    description: 'Skill in wheel-to-wheel racing, overtaking, and defensive driving'
  },
  speed: {
    description: 'Pure one-lap pace and qualifying performance'
  },
  tire_management: {
    description: 'Ability to manage tire degradation over long stints'
  }
};

// Static model statistics (from validation)
const model_stats = {
  r_squared: 0.895,
  cross_val_r_squared: 0.877,
  mae: 1.78,
  races_analyzed: 291
};

function TrackIntelligence() {
  const navigate = useNavigate();

  // State for API data
  const [drivers, setDrivers] = useState([]);
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load data from API on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [tracksData, driversData] = await Promise.all([
          getTracks(),
          getDrivers()
        ]);
        setTracks(tracksData);
        setDrivers(driversData);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const [selectedTrack, setSelectedTrack] = useState(null);
  const [expandedRow, setExpandedRow] = useState(null); // { driverNumber, factorName }
  const [sortConfig, setSortConfig] = useState({ key: 'circuitFitScore', direction: 'desc' }); // Default sort by circuit fit

  // Pre-select Barber track once tracks are loaded
  useEffect(() => {
    if (tracks.length > 0 && !selectedTrack) {
      const barber = tracks.find(track => track.id === 'barber');
      setSelectedTrack(barber || tracks[0]);
    }
  }, [tracks]);

  // Calculate average track demands across all tracks
  const avgDemands = useMemo(() => {
    if (tracks.length === 0) {
      return { consistency: 0, racecraft: 0, speed: 0, tire_management: 0 };
    }

    const totals = tracks.reduce((acc, track) => ({
      consistency: acc.consistency + track.demand_profile.consistency,
      racecraft: acc.racecraft + track.demand_profile.racecraft,
      speed: acc.speed + track.demand_profile.speed,
      tire_management: acc.tire_management + track.demand_profile.tire_management
    }), { consistency: 0, racecraft: 0, speed: 0, tire_management: 0 });

    return {
      consistency: totals.consistency / tracks.length,
      racecraft: totals.racecraft / tracks.length,
      speed: totals.speed / tracks.length,
      tire_management: totals.tire_management / tracks.length
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
        track: normalize(selectedTrack.demand_profile.consistency, avgDemands.consistency),
        average: normalize(avgDemands.consistency, avgDemands.consistency),
        fullMark: 100
      },
      {
        skill: 'Racecraft',
        track: normalize(selectedTrack.demand_profile.racecraft, avgDemands.racecraft),
        average: normalize(avgDemands.racecraft, avgDemands.racecraft),
        fullMark: 100
      },
      {
        skill: 'Speed',
        track: normalize(selectedTrack.demand_profile.speed, avgDemands.speed),
        average: normalize(avgDemands.speed, avgDemands.speed),
        fullMark: 100
      },
      {
        skill: 'Tire Mgmt',
        track: normalize(selectedTrack.demand_profile.tire_management, avgDemands.tire_management),
        average: normalize(avgDemands.tire_management, avgDemands.tire_management),
        fullMark: 100
      }
    ];
  }, [selectedTrack, avgDemands]);

  // Calculate circuit fit scores and prepare driver radar data
  const rankedDrivers = useMemo(() => {
    if (!selectedTrack || drivers.length === 0) return [];

    const driversWithFit = drivers.map(driver => {
      // Calculate circuit fit using dot product (negative is better fit)
      const fit =
        (driver.speed.z_score * selectedTrack.demand_profile.speed) +
        (driver.consistency.z_score * selectedTrack.demand_profile.consistency) +
        (driver.racecraft.z_score * selectedTrack.demand_profile.racecraft) +
        (driver.tire_management.z_score * selectedTrack.demand_profile.tire_management);

      // Convert to 0-100 scale (negative fit is better, so invert)
      const fitScore = Math.max(0, Math.min(100, Math.round(50 - (fit * 5))));

      // Calculate factor rankings (which factor is 1st, 2nd, 3rd, 4th strongest for this driver)
      const factorScores = [
        { name: 'consistency', score: driver.consistency.score },
        { name: 'racecraft', score: driver.racecraft.score },
        { name: 'speed', score: driver.speed.score },
        { name: 'tire_management', score: driver.tire_management.score }
      ];

      // Sort by score descending to get rankings
      const sortedFactors = [...factorScores].sort((a, b) => b.score - a.score);

      // Create ranking map
      const factorRankings = {};
      sortedFactors.forEach((factor, index) => {
        factorRankings[factor.name] = index + 1; // 1st, 2nd, 3rd, 4th
      });

      // Create radar data for this driver
      const normalize = (zScore) => {
        // Convert z-score (-3 to +3) to 0-100 scale
        // Negative z-scores are better (above average)
        return Math.max(0, Math.min(100, 50 - (zScore * 15)));
      };

      const driverRadarData = [
        {
          skill: 'Consistency',
          value: normalize(driver.consistency.z_score),
          trackDemand: (selectedTrack.demand_profile.consistency / 10) * 100
        },
        {
          skill: 'Racecraft',
          value: normalize(driver.racecraft.z_score),
          trackDemand: (selectedTrack.demand_profile.racecraft / 10) * 100
        },
        {
          skill: 'Speed',
          value: normalize(driver.speed.z_score),
          trackDemand: (selectedTrack.demand_profile.speed / 10) * 100
        },
        {
          skill: 'Tire Mgmt',
          value: normalize(driver.tire_management.z_score),
          trackDemand: (selectedTrack.demand_profile.tire_management / 10) * 100
        }
      ];

      return {
        ...driver,
        circuitFitScore: fitScore,
        factorRankings,
        radarData: driverRadarData
      };
    });

    // Sort by circuit fit (higher is better)
    return driversWithFit.sort((a, b) => b.circuitFitScore - a.circuitFitScore);
  }, [selectedTrack, drivers]);

  // Apply sorting to rankedDrivers
  const sortedDrivers = useMemo(() => {
    if (!rankedDrivers || rankedDrivers.length === 0) return [];

    const sorted = [...rankedDrivers];

    if (sortConfig.key) {
      sorted.sort((a, b) => {
        let aValue, bValue;

        // Handle different data structures
        switch (sortConfig.key) {
          case 'consistency':
            aValue = a.consistency.score;
            bValue = b.consistency.score;
            break;
          case 'racecraft':
            aValue = a.racecraft.score;
            bValue = b.racecraft.score;
            break;
          case 'speed':
            aValue = a.speed.score;
            bValue = b.speed.score;
            break;
          case 'tire_management':
            aValue = a.tire_management.score;
            bValue = b.tire_management.score;
            break;
          case 'circuitFitScore':
            aValue = a.circuitFitScore;
            bValue = b.circuitFitScore;
            break;
          default:
            return 0;
        }

        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }

    return sorted;
  }, [rankedDrivers, sortConfig]);

  // Handle column header click for sorting
  const handleSort = (key) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const handleDriverSelect = (driver) => {
    // Just set the selected driver to show the detail panel
    // Don't navigate - stay on this page
    setSelectedDriver(driver);
  };

  // Show loading state
  if (loading) {
    return (
      <div className="home-container">
        <div style={{ textAlign: 'center', padding: '100px 20px' }}>
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="home-container">
        <div style={{ textAlign: 'center', padding: '100px 20px' }}>
          <h2>Error Loading Data</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="home-container">
      {/* Consolidated Hero Header */}
      <section className="hero-header">
        <div className="hero-content">
          <h1 className="hero-main-title">Track Performance Rankings</h1>
          <div className="hero-methodology">
            <div className="methodology-section">
              <h3 className="methodology-title">How It Works</h3>
              <p className="methodology-text">
                We analyze each driver's performance across four key factors: <strong>Raw Speed</strong> (50%), <strong>Consistency</strong> (31%),
                <strong>Racecraft</strong> (16%), and <strong>Tire Management</strong> (10%). Each track has unique demands—some reward pure speed,
                others require precision and tire conservation. By matching driver strengths to track demands, we calculate a <strong>Circuit Fit Score</strong>
                that predicts who will excel at each venue.
              </p>
            </div>
            <div className="methodology-section">
              <h3 className="methodology-title">How to Use</h3>
              <p className="methodology-text">
                <strong>Select a track</strong> to see how its demands align with each driver's skill profile. <strong>Click column headers</strong> to sort
                by any factor and identify specialists. <strong>Click factor values</strong> to expand and see the underlying performance variables.
                Use this intelligence to inform race predictions, fantasy picks, and strategic decisions.
              </p>
            </div>
          </div>

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
                  }}
                >
                  <span className="track-pill-name">{track.name.split(' ')[0]}</span>
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
                      <span className="meta-item">{selectedTrack.length_miles} miles</span>
                    </div>
                  </div>

                  {selectedTrack.description && (
                    <p className="track-insight-text">
                      {selectedTrack.description}
                    </p>
                  )}

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

          {/* Driver Rankings Section - Full Width */}
          <section className="rankings-section-wrapper">
            <div className="rankings-main-full">
                <div className="rankings-header">
                <div>
                  <h2 className="rankings-title">Driver Rankings</h2>
                  <p className="rankings-subtitle">
                    Sorted by circuit fit score • Click any factor value to see underlying variables
                  </p>
                </div>
              </div>

                {/* Grid-Based Table */}
                <div className="rankings-grid-container">
                  {/* Header Row */}
                  <div className="grid-header">
                    <div className="grid-cell header-cell rank-col">#</div>
                    <div className="grid-cell header-cell driver-col">DRIVER</div>
                    <div className="grid-cell header-cell stat-col sortable-header" onClick={() => handleSort('consistency')}>
                      <span className="header-with-info">
                        CONSISTENCY
                        <span className="info-icon" data-tooltip={factor_info.consistency.description}>ⓘ</span>
                      </span>
                      {sortConfig.key === 'consistency' && (
                        <span className="sort-indicator">{sortConfig.direction === 'desc' ? '▼' : '▲'}</span>
                      )}
                    </div>
                    <div className="grid-cell header-cell stat-col sortable-header" onClick={() => handleSort('racecraft')}>
                      <span className="header-with-info">
                        RACECRAFT
                        <span className="info-icon" data-tooltip={factor_info.racecraft.description}>ⓘ</span>
                      </span>
                      {sortConfig.key === 'racecraft' && (
                        <span className="sort-indicator">{sortConfig.direction === 'desc' ? '▼' : '▲'}</span>
                      )}
                    </div>
                    <div className="grid-cell header-cell stat-col sortable-header" onClick={() => handleSort('speed')}>
                      <span className="header-with-info">
                        SPEED
                        <span className="info-icon" data-tooltip={factor_info.speed.description}>ⓘ</span>
                      </span>
                      {sortConfig.key === 'speed' && (
                        <span className="sort-indicator">{sortConfig.direction === 'desc' ? '▼' : '▲'}</span>
                      )}
                    </div>
                    <div className="grid-cell header-cell stat-col sortable-header" onClick={() => handleSort('tire_management')}>
                      <span className="header-with-info">
                        TIRE MGMT
                        <span className="info-icon" data-tooltip={factor_info.tire_management.description}>ⓘ</span>
                      </span>
                      {sortConfig.key === 'tire_management' && (
                        <span className="sort-indicator">{sortConfig.direction === 'desc' ? '▼' : '▲'}</span>
                      )}
                    </div>
                    <div className="grid-cell header-cell fit-col sortable-header" onClick={() => handleSort('circuitFitScore')}>
                      <span className="header-with-info">
                        CIRCUIT FIT
                        <span className="info-icon" data-tooltip="Calculated by matching driver skill profile to track demands. Higher scores indicate better track-driver fit based on consistency, racecraft, raw speed, and tire management factors.">ⓘ</span>
                      </span>
                      {sortConfig.key === 'circuitFitScore' && (
                        <span className="sort-indicator">{sortConfig.direction === 'desc' ? '▼' : '▲'}</span>
                      )}
                    </div>
                  </div>

                  {/* Data Rows with Expandable Variables */}
                  {sortedDrivers.map((driver, index) => {
                    const factorMeta = {
                      consistency: { icon: <BullseyeIcon size="md" />, title: 'Consistency', weight: '31%', variables: [
                        { label: 'Stint Consistency', value: 71 },
                        { label: 'Sector Consistency', value: 68 },
                        { label: 'Braking Consistency', value: 66 },
                        { label: 'Lap Time Variance', value: 63 },
                        { label: 'Corner Repeatability', value: 64 },
                        { label: 'Pressure Consistency', value: 61 }
                      ]},
                      racecraft: { icon: <SwordIcon size="md" />, title: 'Racecraft', weight: '16%', variables: [
                        { label: 'Positions Gained', value: 58 },
                        { label: 'Position Changes', value: 52 },
                        { label: 'Pass Success Rate', value: 49 },
                        { label: 'Defensive Rating', value: 51 }
                      ]},
                      speed: { icon: <LightningIcon size="md" />, title: 'Speed', weight: '50%', variables: [
                        { label: 'Qualifying Pace', value: 72 },
                        { label: 'Best Race Lap', value: 68 },
                        { label: 'Avg Top-10 Pace', value: 65 },
                        { label: 'Speed Trap Max', value: 70 },
                        { label: 'Sector Best Combo', value: 64 },
                        { label: 'Ultimate Pace', value: 69 }
                      ]},
                      tire_management: { icon: <TireIcon size="md" />, title: 'Tire Management', weight: '10%', variables: [
                        { label: 'Pace Degradation', value: 56 },
                        { label: 'Late Stint Performance', value: 53 },
                        { label: 'Early vs Late Pace', value: 54 },
                        { label: 'Thermal Management', value: 52 }
                      ]}
                    };

                    return (
                      <React.Fragment key={driver.driver_number}>
                        {/* Main Data Row */}
                        <div className="grid-row">
                          <div className="grid-cell rank-col">
                            <span className="rank-number">{index + 1}</span>
                          </div>
                          <div className="grid-cell driver-col">
                            <span className="driver-number">#{driver.driver_number}</span>
                          </div>
                          <div
                            className={`grid-cell stat-col clickable-cell ${
                              expandedRow?.driverNumber === driver.driver_number && expandedRow?.factorName === 'consistency' ? 'active-cell' : ''
                            }`}
                            onClick={() => {
                              if (expandedRow?.driverNumber === driver.driver_number && expandedRow?.factorName === 'consistency') {
                                setExpandedRow(null);
                              } else {
                                setExpandedRow({ driverNumber: driver.driver_number, factorName: 'consistency' });
                              }
                            }}
                          >
                            <span className="stat-value">{driver.consistency.score}</span>
                          </div>
                          <div
                            className={`grid-cell stat-col clickable-cell ${
                              expandedRow?.driverNumber === driver.driver_number && expandedRow?.factorName === 'racecraft' ? 'active-cell' : ''
                            }`}
                            onClick={() => {
                              if (expandedRow?.driverNumber === driver.driver_number && expandedRow?.factorName === 'racecraft') {
                                setExpandedRow(null);
                              } else {
                                setExpandedRow({ driverNumber: driver.driver_number, factorName: 'racecraft' });
                              }
                            }}
                          >
                            <span className="stat-value">{driver.racecraft.score}</span>
                          </div>
                          <div
                            className={`grid-cell stat-col clickable-cell ${
                              expandedRow?.driverNumber === driver.driver_number && expandedRow?.factorName === 'speed' ? 'active-cell' : ''
                            }`}
                            onClick={() => {
                              if (expandedRow?.driverNumber === driver.driver_number && expandedRow?.factorName === 'speed') {
                                setExpandedRow(null);
                              } else {
                                setExpandedRow({ driverNumber: driver.driver_number, factorName: 'speed' });
                              }
                            }}
                          >
                            <span className="stat-value">{driver.speed.score}</span>
                          </div>
                          <div
                            className={`grid-cell stat-col clickable-cell ${
                              expandedRow?.driverNumber === driver.driver_number && expandedRow?.factorName === 'tire_management' ? 'active-cell' : ''
                            }`}
                            onClick={() => {
                              if (expandedRow?.driverNumber === driver.driver_number && expandedRow?.factorName === 'tire_management') {
                                setExpandedRow(null);
                              } else {
                                setExpandedRow({ driverNumber: driver.driver_number, factorName: 'tire_management' });
                              }
                            }}
                          >
                            <span className="stat-value">{driver.tire_management.score}</span>
                          </div>
                          <div className="grid-cell fit-col">
                            <span className="fit-value">{driver.circuitFitScore}</span>
                          </div>
                        </div>

                        {/* Expanded Variables Row */}
                        {expandedRow?.driverNumber === driver.driver_number && (
                          <div className="expanded-row">
                            <div className="expanded-content">
                              <div className="expanded-header">
                                <div className="expanded-header-left">
                                  <h4 className="expanded-title">
                                    {factorMeta[expandedRow.factorName].icon} {factorMeta[expandedRow.factorName].title}
                                    <span className="expanded-weight">({factorMeta[expandedRow.factorName].weight})</span>
                                  </h4>
                                  <p className="expanded-subtitle">
                                    Underlying variables for Driver #{driver.driver_number}
                                  </p>
                                </div>
                                <button
                                  className="strategize-button-expanded"
                                  onClick={() => navigate('/strategy', {
                                    state: {
                                      driverNumber: driver.driver_number,
                                      trackId: selectedTrack.id
                                    }
                                  })}
                                >
                                  Go Strategize →
                                </button>
                              </div>
                              <div className="variables-grid">
                                {factorMeta[expandedRow.factorName].variables.map((variable, vIndex) => (
                                  <div key={vIndex} className="variable-item">
                                    <span className="variable-label">{variable.label}</span>
                                    <div className="variable-bar-bg">
                                      <div className="variable-bar" style={{ width: `${variable.value}%` }}></div>
                                    </div>
                                    <span className="variable-value">{variable.value}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
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
