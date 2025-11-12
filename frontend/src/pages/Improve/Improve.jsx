/**
 * Improve Page - Skill Development and Performance Analysis
 * Match skills with similar drivers and track performance improvement areas
 */

import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import SkillSliders from './components/SkillSliders';
import PerformanceAnalysis from './components/PerformanceAnalysis';
import './Improve.css';

export default function Improve() {
  const { selectedDriverNumber, drivers } = useDriver();

  const [driverData, setDriverData] = useState(null);
  const [coachingData, setCoachingData] = useState(null);
  const [targetSkills, setTargetSkills] = useState(null);
  const [similarDrivers, setSimilarDrivers] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);

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
          `/api/drivers/${selectedDriverNumber}/telemetry-coaching`,
          {
            params: {
              track_id: 'barber',
              race_num: 1
            }
          }
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
        <DashboardHeader driverData={driverData} pageName="Improve" />
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
      <DashboardHeader driverData={driverData} pageName="Improve" />

      {/* Unified Navigation Tabs */}
      <DashboardTabs />

      {/* Main Content Grid */}
      <div className="improve-grid">

        {/* SKILL SLIDERS SECTION */}
        {driverData && (
          <section className="skill-sliders-section">
            <SkillSliders
              currentSkills={{
                speed: driverData.speed?.score || 0,
                consistency: driverData.consistency?.score || 0,
                racecraft: driverData.racecraft?.score || 0,
                tire_management: driverData.tire_management?.score || 0
              }}
              onTargetChange={handleTargetChange}
              onFindSimilar={handleFindSimilar}
            />
          </section>
        )}

        {/* SIMILAR DRIVERS LOADING */}
        {searching && (
          <section className="similar-drivers-loading">
            <div className="loading-text">Finding similar drivers...</div>
          </section>
        )}

        {/* SIMILAR DRIVERS RESULTS */}
        {similarDrivers && similarDrivers.length > 0 && driverData && (
          <section className="similar-drivers-section">
            {/* Improvement Prediction */}
            <div className="improvement-prediction">
              <h4>YOUR PREDICTED IMPROVEMENT</h4>
              <div className="improvement-stats">
                <div className="stat-box">
                  <div className="stat-label">Current Avg</div>
                  <div className="stat-value current">
                    {driverData.stats?.average_finish?.toFixed(2) || 'N/A'}
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
                      return avgOfSimilar ? avgOfSimilar.toFixed(2) : 'N/A';
                    })()}
                  </div>
                  {(() => {
                    const current = driverData.stats?.average_finish;
                    const avgOfSimilar = similarDrivers
                      .filter(d => d.avg_finish)
                      .reduce((sum, d) => sum + d.avg_finish, 0) /
                      similarDrivers.filter(d => d.avg_finish).length;
                    if (current && avgOfSimilar) {
                      const improvement = current - avgOfSimilar;
                      return (
                        <div className="improvement-delta">
                          {improvement > 0 ? `↑ ${improvement.toFixed(2)} positions better` : 'No change'}
                        </div>
                      );
                    }
                    return null;
                  })()}
                </div>
              </div>
            </div>

            <div className="similar-drivers-header">
              <h3>Top 3 Similar Drivers</h3>
              <p className="similar-drivers-subtitle">
                Drivers with skill patterns most similar to your target
              </p>
            </div>

            <div className="similar-drivers-grid">
              {similarDrivers.map((driver, index) => (
                <div key={driver.driver_number} className="similar-driver-card">
                  <div className="rank-badge">#{index + 1}</div>
                  <div className="match-score">{driver.match_score}% Match</div>

                  <div className="driver-info">
                    <h4>Driver #{driver.driver_number}</h4>
                    <p>{driver.driver_name}</p>
                  </div>

                  {driver.avg_finish && (
                    <div className="avg-finish">
                      <span className="label">Avg Finish:</span>
                      <span className="value">{driver.avg_finish}</span>
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
          </section>
        )}

        {/* PERFORMANCE ANALYSIS SECTION */}
        <PerformanceAnalysis
          coachingData={coachingData}
          driverData={driverData}
        />

      </div>
    </div>
  );
}
