/**
 * Improve Page - Achievements, Training Programs, and Performance Analysis
 * Design matches mockup with 3 main sections
 */

import { useState, useEffect } from 'react';
import api from '../../services/api';
import { useDriver } from '../../context/DriverContext';
import DashboardHeader from '../../components/DashboardHeader/DashboardHeader';
import DashboardTabs from '../../components/DashboardTabs/DashboardTabs';
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
  const [loading, setLoading] = useState(true);
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
                  {achievement.unlocked ? '🏆' : '🔒'}
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
                <div className="note-icon">💡</div>
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
                <h3>⚠️ Priority Areas</h3>
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
                  <h3>✓ Top Strengths</h3>
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
