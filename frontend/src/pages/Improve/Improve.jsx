/**
 * Development Page - Projection and Planning View
 * Interactive skill projections showing where driver would rank with improvements
 * Includes practice plan generation and similar driver matching
 */

import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import SkillSliders from './components/SkillSliders';
import PerformanceAnalysis from './components/PerformanceAnalysis';
import PracticePlanGenerator from './components/PracticePlanGenerator';
import ProjectedRankingsTable from '../../components/ProjectedRankingsTable/ProjectedRankingsTable';
import './Improve.css';

export default function Improve() {
  const { selectedDriverNumber, drivers } = useDriver();

  const [driverData, setDriverData] = useState(null);
  const [coachingData, setCoachingData] = useState(null);
  const [targetSkills, setTargetSkills] = useState(null);
  const [similarDrivers, setSimilarDrivers] = useState(null);
  const [selectedTrack, setSelectedTrack] = useState('barber');
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);

  const tracks = [
    { id: 'barber', name: 'Barber Motorsports Park' },
    { id: 'cota', name: 'Circuit of the Americas' },
    { id: 'roadamerica', name: 'Road America' },
    { id: 'sebring', name: 'Sebring International' },
    { id: 'sonoma', name: 'Sonoma Raceway' },
    { id: 'vir', name: 'Virginia International Raceway' }
  ];

  // Load driver data and coaching
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get driver data
        const driverResponse = await api.get(`/api/drivers/${selectedDriverNumber}`);
        setDriverData(driverResponse.data);

        // Get telemetry coaching for Barber
        const coachingResponse = await api.get(
          `/api/drivers/${selectedDriverNumber}/telemetry-coaching?track_id=barber&race_num=1`
        );
        setCoachingData(coachingResponse.data);

      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load performance data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedDriverNumber]);


  // Handle target skills change from sliders
  const handleTargetChange = (newTargets) => {
    setTargetSkills(newTargets);
  };

  // Find similar drivers based on target skills
  const handleFindSimilar = async () => {
    if (!targetSkills) return;

    try {
      setSearching(true);
      setSimilarDrivers(null);

      // Call backend API to find top 3 similar drivers
      const response = await api.post('/api/drivers/find-similar', {
        current_driver_number: selectedDriverNumber,
        target_skills: targetSkills
      });

      setSimilarDrivers(response.data.similar_drivers);
    } catch (err) {
      console.error('Error finding similar drivers:', err);
      setError('Failed to find similar drivers. Please try again.');
    } finally {
      setSearching(false);
    }
  };

  if (loading) {
    return (
      <div className="improve-page">
        <DashboardHeader driverData={driverData} pageName="Development" />
        <DashboardTabs />
        <div className="loading-container">
          <div className="loading-text">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="improve-page">
      {/* Unified Header */}
      <DashboardHeader driverData={driverData} pageName="Development" />

      {/* Unified Navigation Tabs */}
      <DashboardTabs />

      {/* Main Content */}
      <div className="improve-content">

        {/* Connection to Skills Page */}
        <div className="skills-connection-banner">
          <div className="banner-content">
            <span className="banner-icon" aria-hidden="true">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e65100" strokeWidth="2">
                <path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z"/>
                <line x1="9" y1="21" x2="15" y2="21"/>
              </svg>
            </span>
            <span className="banner-text">
              <strong>Tip:</strong> Visit the <strong>Skills</strong> page first to see your prioritized weakness analysis
              and coach recommendations. Then come here to project where you could rank with those improvements!
            </span>
          </div>
        </div>

        {/* PROJECTED RANKINGS - THE KILLER FEATURE */}
        {driverData && targetSkills && (
          <section className="projected-rankings-section">
            <div className="section-header">
              <h2>Projected Rankings</h2>
              <p>See where you would rank with your adjusted skills</p>
            </div>
            <ProjectedRankingsTable
              driverNumber={selectedDriverNumber}
              adjustedSkills={{
                speed: targetSkills.speed,
                consistency: targetSkills.consistency,
                racecraft: targetSkills.racecraft,
                tire_management: targetSkills.tire_management,
              }}
              onProjectionUpdate={(projection) => {
                console.log('Projection updated:', projection);
              }}
            />
          </section>
        )}

        {/* TWO COLUMN LAYOUT - Skills & Comparables */}
        <div className="improve-grid">
          {/* LEFT COLUMN - SKILL SLIDERS */}
          {driverData && (
            <section className="skill-sliders-section">
              <SkillSliders
                currentSkills={{
                  speed: driverData.speed?.percentile || 0,
                  consistency: driverData.consistency?.percentile || 0,
                  racecraft: driverData.racecraft?.percentile || 0,
                  tire_management: driverData.tire_management?.percentile || 0
                }}
                onTargetChange={handleTargetChange}
                onFindSimilar={handleFindSimilar}
                tracks={tracks}
                selectedTrack={selectedTrack}
                onTrackChange={setSelectedTrack}
              />
            </section>
          )}

          {/* RIGHT COLUMN - COMPARABLES */}
          <section className="comparables-section">
            {!searching && !similarDrivers && (
              <div className="comparables-empty">
                <div className="empty-icon" aria-hidden="true">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#999" strokeWidth="1.5">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <h3>Find Similar Drivers</h3>
                <p>Adjust your target skills and select a track, then click "Find Comparables" to see drivers with similar skill profiles.</p>
              </div>
            )}

            {searching && (
              <div className="comparables-loading">
                <div className="loading-spinner"></div>
                <p>Finding similar drivers...</p>
              </div>
            )}

            {similarDrivers && similarDrivers.length > 0 && driverData && (
              <div className="comparables-results">
                <div className="comparables-header">
                  <h3>Similar Drivers at {tracks.find(t => t.id === selectedTrack)?.name}</h3>
                  <p>Drivers with skill patterns most similar to your target</p>
                </div>

                {/* Improvement Prediction */}
                <div className="improvement-prediction">
                  <h4>Predicted Improvement</h4>
                  <div className="improvement-stats">
                    <div className="stat-box">
                      <div className="stat-label">Current Avg</div>
                      <div className="stat-value current">
                        {driverData.stats?.average_finish?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                    <div className="stat-arrow">→</div>
                    <div className="stat-box">
                      <div className="stat-label">Predicted Avg</div>
                      <div className="stat-value predicted">
                        {(() => {
                          const avgOfSimilar = similarDrivers
                            .filter(d => d.avg_finish)
                            .reduce((sum, d) => sum + d.avg_finish, 0) /
                            similarDrivers.filter(d => d.avg_finish).length;
                          return avgOfSimilar ? avgOfSimilar.toFixed(1) : 'N/A';
                        })()}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Similar Drivers List */}
                <div className="similar-drivers-list">
                  {similarDrivers.map((driver, index) => (
                    <div key={driver.driver_number} className="similar-driver-card">
                      <div className="rank-badge">#{index + 1}</div>
                      <div className="driver-info">
                        <h4>Driver #{driver.driver_number}</h4>
                        <p>{driver.driver_name}</p>
                        <div className="match-score">{driver.match_score}% Match</div>
                      </div>
                      {driver.avg_finish && (
                        <div className="avg-finish">
                          <span className="label">Avg Finish</span>
                          <span className="value">P{driver.avg_finish.toFixed(1)}</span>
                        </div>
                      )}
                      <div className="skills-grid">
                        <div className="skill-item">
                          <span className="skill-label">Speed</span>
                          <span className="skill-value">{driver.skills.speed}</span>
                        </div>
                        <div className="skill-item">
                          <span className="skill-label">Consistency</span>
                          <span className="skill-value">{driver.skills.consistency}</span>
                        </div>
                        <div className="skill-item">
                          <span className="skill-label">Racecraft</span>
                          <span className="skill-value">{driver.skills.racecraft}</span>
                        </div>
                        <div className="skill-item">
                          <span className="skill-label">Tire Mgmt</span>
                          <span className="skill-value">{driver.skills.tire_management}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </div>

        {/* FULL WIDTH SECTIONS BELOW */}
        {/* PRACTICE PLAN GENERATOR */}
        {driverData && (
          <section className="practice-plan-section">
            <PracticePlanGenerator driverData={driverData} api={api} />
          </section>
        )}

        {/* PERFORMANCE ANALYSIS SECTION */}
        <section className="performance-analysis-section">
          <PerformanceAnalysis
            coachingData={coachingData}
            driverData={driverData}
          />
        </section>

      </div>
    </div>
  );
}
