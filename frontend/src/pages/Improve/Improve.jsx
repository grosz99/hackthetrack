/**
 * Improve Page - Achievements, Training Programs, and Performance Analysis
 * Design matches mockup with 3 main sections
 */

import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
import SkillSliders from './components/SkillSliders';
import './Improve.css';

// Mock achievements data (TODO: Move to backend)
const ACHIEVEMENTS = [
  { id: 'speed_demon', name: 'Speed Demon', description: 'Reach 80+ Speed', unlocked: false },
  { id: 'corner_master', name: 'Corner Master', description: 'Reach 80+ Cornering', unlocked: false },
  { id: 'consistent_driver', name: 'Consistent Driver', description: 'Reach 70+ Consistency', unlocked: false },
  { id: 'rain_master', name: 'Rain Master', description: 'Reach 75+ Wet Weather', unlocked: false },
  { id: 'elite_racer', name: 'Elite Racer', description: 'Overall Rating 85+', unlocked: false },
  { id: 'all_rounder', name: 'All-Rounder', description: 'All skills above 70', unlocked: false }
];

// Mock training programs (TODO: Move to backend)
const TRAINING_PROGRAMS = [
  {
    id: 'precision_driving',
    name: 'Precision Driving',
    duration: '2 weeks',
    xp: 500,
    skills: ['Cornering', 'Braking'],
    recommended: true
  },
  {
    id: 'race_strategy',
    name: 'Race Strategy',
    duration: '3 weeks',
    xp: 750,
    skills: ['Racecraft', 'Consistency']
  },
  {
    id: 'wet_weather',
    name: 'Wet Weather Specialist',
    duration: '1 week',
    xp: 400,
    skills: ['Wet Weather']
  },
  {
    id: 'speed_aggression',
    name: 'Speed & Aggression',
    duration: '2 weeks',
    xp: 600,
    skills: ['Top Speed', 'Overtaking']
  }
];

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

  // Calculate top strengths from driver data
  const getTopStrengths = () => {
    if (!driverData) return [];

    const factors = [
      { name: 'Cornering', value: driverData.racecraft?.score || 0 },
      { name: 'Racecraft', value: driverData.racecraft?.score || 0 },
      { name: 'Speed', value: driverData.speed?.score || 0 },
      { name: 'Consistency', value: driverData.consistency?.score || 0 },
      { name: 'Tire Management', value: driverData.tire_management?.score || 0 }
    ];

    return factors
      .filter(f => f.value >= 70)
      .sort((a, b) => b.value - a.value)
      .slice(0, 2);
  };

  // Calculate priority areas from coaching data
  const getPriorityAreas = () => {
    if (!coachingData || !coachingData.factor_breakdown) return [];

    return Object.entries(coachingData.factor_breakdown)
      .map(([factor, count]) => ({
        name: factor,
        value: 100 - (count * 10), // Convert to score (more issues = lower score)
        points: count * 10
      }))
      .sort((a, b) => b.points - a.points)
      .slice(0, 2);
  };

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

  const topStrengths = getTopStrengths();
  const priorityAreas = getPriorityAreas();

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

        {/* ACHIEVEMENTS SECTION */}
        <section className="achievements-section">
          <div className="section-header">
            <h2>ACHIEVEMENTS</h2>
            <div className="badge-count">
              <span className="count-number">0</span>
              <span className="count-label">BADGES</span>
            </div>
          </div>

          <div className="achievements-grid">
            {ACHIEVEMENTS.map(achievement => (
              <div key={achievement.id} className={`achievement-card ${achievement.unlocked ? 'unlocked' : 'locked'}`}>
                <div className="achievement-icon">
                  {achievement.unlocked ? 'UNLOCKED' : 'LOCKED'}
                </div>
                <div className="achievement-name">{achievement.name}</div>
                <div className="achievement-desc">{achievement.description}</div>
              </div>
            ))}
          </div>
        </section>

        {/* TRAINING PROGRAMS SECTION */}
        <section className="training-section">
          <div className="section-header">
            <h2>TRAINING PROGRAMS</h2>
            <p className="section-subtitle">Complete programs to earn XP and improve skills</p>
          </div>

          <div className="programs-list">
            {TRAINING_PROGRAMS.map(program => (
              <div key={program.id} className="program-card">
                <div className="program-header">
                  <h3>{program.name}</h3>
                  {program.recommended && <span className="recommended-badge">RECOMMENDED</span>}
                </div>
                <div className="program-details">
                  <span>{program.duration}</span>
                  <span>+{program.xp} XP</span>
                </div>
                <div className="program-skills">
                  {program.skills.map(skill => (
                    <span key={skill} className="skill-tag">{skill}</span>
                  ))}
                </div>
                <button className="program-button">
                  {program.recommended ? 'Start Training' : 'View Program'}
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* PERFORMANCE ANALYSIS SECTION */}
        <section className="performance-section">
          <div className="section-header">
            <h2>PERFORMANCE ANALYSIS</h2>
            <p className="section-subtitle">Focus areas for maximum improvement</p>
          </div>

          {error && (
            <div className="error-message">{error}</div>
          )}

          {coachingData && (
            <>
              {/* Team Principal's Note */}
              <div className="team-note">
                <div className="note-content">
                  <h3>Team Principal's Note</h3>
                  <p>
                    {coachingData.summary.primary_weakness ?
                      `Focus on ${coachingData.summary.primary_weakness} - you're ${coachingData.summary.corners_need_work}/${coachingData.summary.total_corners} corners off pace at Barber` :
                      "Strong development! You're showing real potential. Continue building your weaker skills."
                    }
                  </p>
                </div>
              </div>

              {/* Priority Areas */}
              <div className="priority-areas">
                <h3>PRIORITY AREAS</h3>
                {priorityAreas.map(area => (
                  <div key={area.name} className="priority-item">
                    <div className="priority-header">
                      <span className="priority-name">{area.name}</span>
                      <span className="priority-score">{area.value}</span>
                    </div>
                    <div className="priority-bar">
                      <div
                        className="priority-fill"
                        style={{width: `${area.value}%`}}
                      ></div>
                    </div>
                    <div className="priority-text">+{area.points} points to reach competitive level</div>
                  </div>
                ))}
              </div>

              {/* Top Strengths */}
              {topStrengths.length > 0 && (
                <div className="top-strengths">
                  <h3>TOP STRENGTHS</h3>
                  {topStrengths.map(strength => (
                    <div key={strength.name} className="strength-item">
                      <span className="strength-name">{strength.name}</span>
                      <span className="strength-score">{Math.round(strength.value)}</span>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </section>

      </div>
    </div>
  );
}
