/**
 * Improve Page - Driver Skill Improvement Lab
 *
 * Allows drivers to adjust their skills and see:
 * - Who they'd be like with those adjusted skills
 * - What their predicted performance would be
 * - Specific recommendations for improvement
 *
 * Uses statistically validated prediction model with 1-point budget.
 */

import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import api from '../services/api';
import './Improve.css';

const POINTS_BUDGET = 1.0;

// Map internal factor names to display names
const FACTOR_DISPLAY_NAMES = {
  'speed': 'Raw Speed',
  'consistency': 'Consistency',
  'racecraft': 'Racecraft',
  'tire_management': 'Tire Management'
};

// Factor descriptions
const FACTOR_DESCRIPTIONS = {
  'speed': 'Raw Speed',
  'consistency': 'Mental Focus',
  'racecraft': 'Race Positioning',
  'tire_management': 'Technical Skill'
};

export default function Improve() {
  const [driverNumber, setDriverNumber] = useState(13);
  const [drivers] = useState([
    { number: 13, name: 'Driver #13' },
    { number: 7, name: 'Driver #7' },
    { number: 5, name: 'Driver #5' },
    { number: 88, name: 'Driver #88' },
    { number: 15, name: 'Driver #15' },
  ]);

  const [driverData, setDriverData] = useState(null);
  const [currentSkills, setCurrentSkills] = useState(null);
  const [adjustedSkills, setAdjustedSkills] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);

  // Load driver data
  useEffect(() => {
    const fetchDriverData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await api.get(`/api/drivers/${driverNumber}`);
        setDriverData(response.data);

        // Initialize current and adjusted skills
        const skills = {
          speed: response.data.speed.percentile,
          consistency: response.data.consistency.percentile,
          racecraft: response.data.racecraft.percentile,
          tire_management: response.data.tire_management.percentile
        };

        setCurrentSkills(skills);
        setAdjustedSkills({...skills});

        // Get initial prediction
        await fetchPrediction(skills);

      } catch (err) {
        console.error('Error fetching driver data:', err);
        setError('Failed to load driver data');
      } finally {
        setLoading(false);
      }
    };

    fetchDriverData();
  }, [driverNumber]);

  // Fetch prediction from API
  const fetchPrediction = async (skills) => {
    try {
      setUpdating(true);
      const response = await api.post(
        `/api/drivers/${driverNumber}/improve/predict`,
        skills
      );
      setPrediction(response.data);
    } catch (err) {
      console.error('Error fetching prediction:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      }
    } finally {
      setUpdating(false);
    }
  };

  // Adjust skill value
  const adjustSkill = (factor, delta) => {
    if (!adjustedSkills || !currentSkills) return;

    const newValue = Math.max(0, Math.min(100, adjustedSkills[factor] + delta));
    const newSkills = { ...adjustedSkills, [factor]: newValue };

    // Calculate points used
    const pointsUsed = Object.keys(newSkills).reduce((sum, key) => {
      return sum + Math.abs(newSkills[key] - currentSkills[key]);
    }, 0);

    // Check budget
    if (pointsUsed > POINTS_BUDGET) {
      setError(`Cannot exceed ${POINTS_BUDGET} point budget`);
      return;
    }

    setError(null);
    setAdjustedSkills(newSkills);

    // Debounce API call
    clearTimeout(window.improvePredictionTimeout);
    window.improvePredictionTimeout = setTimeout(() => {
      fetchPrediction(newSkills);
    }, 500);
  };

  // Reset to current skills
  const resetSkills = () => {
    if (!currentSkills) return;
    setAdjustedSkills({...currentSkills});
    setError(null);
    fetchPrediction(currentSkills);
  };

  // Calculate points used and available
  const pointsUsed = currentSkills && adjustedSkills
    ? Object.keys(adjustedSkills).reduce((sum, key) => {
        return sum + Math.abs(adjustedSkills[key] - currentSkills[key]);
      }, 0)
    : 0;
  const pointsAvailable = POINTS_BUDGET - pointsUsed;

  if (loading) {
    return (
      <div className="improve-page">
        <div className="loading-container">
          <div className="loading-text">Loading...</div>
        </div>
      </div>
    );
  }

  if (!driverData || !currentSkills || !adjustedSkills) {
    return (
      <div className="improve-page">
        <div className="error-container">
          <div className="error-text">{error || 'No data available'}</div>
        </div>
      </div>
    );
  }

  const topDriver = prediction?.similar_drivers?.[0];

  return (
    <div className="improve-page">
      {/* Header */}
      <div className="improve-header">
        <div className="header-content">
          <div className="driver-number-display">
            <span className="number-large">{driverNumber}</span>
          </div>
          <div className="header-title-section">
            <h1>Driver Skill Improvement Lab</h1>
            <p className="header-subtitle">
              Adjust your skills by ±{POINTS_BUDGET} points to see who you'd be like and what to work on
            </p>
          </div>

          {/* Driver Selector */}
          <div style={{ marginLeft: 'auto' }}>
            <select
              value={driverNumber}
              onChange={(e) => setDriverNumber(Number(e.target.value))}
              className="driver-select"
            >
              {drivers.map((driver) => (
                <option key={driver.number} value={driver.number}>
                  {driver.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="nav-tabs-container">
        <div className="nav-tabs">
          <NavLink to="/overview" className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}>
            Overview
          </NavLink>
          <NavLink to="/race-log" className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}>
            Race Log
          </NavLink>
          <NavLink to="/skills" className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}>
            Skills
          </NavLink>
          <NavLink to="/improve" className={({ isActive }) => `tab ${isActive ? 'active' : ''}`}>
            Improve
          </NavLink>
        </div>
      </div>

      {/* Main Content */}
      <div className="improve-content">
        {/* Left Side: Skill Adjustments */}
        <div className="adjust-skills-section">
          <div className="section-header-row">
            <h2>Adjust Your Skills</h2>
            <div className="points-budget">
              <span className="budget-label">Available Points</span>
              <span className="budget-value">{pointsAvailable.toFixed(1)}</span>
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Skill Sliders */}
          <div className="skills-adjust-list">
            {Object.keys(FACTOR_DISPLAY_NAMES).map((factor) => {
              const displayName = FACTOR_DISPLAY_NAMES[factor];
              const description = FACTOR_DESCRIPTIONS[factor];
              const currentValue = adjustedSkills[factor];
              const originalValue = currentSkills[factor];
              const delta = currentValue - originalValue;

              return (
                <div key={factor} className="skill-adjust-item">
                  <div className="skill-adjust-header">
                    <div>
                      <h3>{displayName}</h3>
                      <p className="skill-description">{description}</p>
                    </div>
                    <div className="skill-value-display">
                      {currentValue.toFixed(1)}
                    </div>
                  </div>

                  <div className="skill-progress-bar">
                    <div
                      className="skill-progress-fill"
                      style={{ width: `${currentValue}%` }}
                    ></div>
                  </div>

                  <div className="skill-controls">
                    <button
                      className="skill-btn skill-btn-minus"
                      onClick={() => adjustSkill(factor, -0.1)}
                      disabled={updating}
                    >
                      −
                    </button>
                    <div className="skill-change-display">
                      {delta > 0 && <span className="skill-increase">+{delta.toFixed(1)}</span>}
                      {delta < 0 && <span className="skill-decrease">{delta.toFixed(1)}</span>}
                      {delta === 0 && <span className="skill-unchanged">—</span>}
                    </div>
                    <button
                      className="skill-btn skill-btn-plus"
                      onClick={() => adjustSkill(factor, 0.1)}
                      disabled={updating}
                    >
                      +
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <button className="reset-btn" onClick={resetSkills} disabled={updating}>
            Reset to Current
          </button>
        </div>

        {/* Right Side: Predictions & Recommendations */}
        <div className="predictions-section">
          {/* You'd Be Like... */}
          {topDriver && (
            <div className="similar-driver-card">
              <h2>You'd Be Like...</h2>

              <div className="top-driver-info">
                <div className="driver-match-header">
                  <h3>{topDriver.driver_name}</h3>
                  <div className="match-percentage">
                    {topDriver.match_percentage.toFixed(0)}%
                    <span className="match-label">Match</span>
                  </div>
                </div>

                {topDriver.key_strengths && topDriver.key_strengths.length > 0 && (
                  <div className="key-strengths">
                    <span className="strengths-label">Key Strengths:</span>
                    <ul className="strengths-list">
                      {topDriver.key_strengths.map((strength, idx) => (
                        <li key={idx}>{strength}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* All Comparable Drivers */}
              {prediction.similar_drivers && prediction.similar_drivers.length > 1 && (
                <div className="all-comparisons">
                  <h4>All Driver Comparisons:</h4>
                  <div className="comparison-list">
                    {prediction.similar_drivers.map((driver, idx) => (
                      <div key={idx} className="comparison-item">
                        <span className="comparison-name">{driver.driver_name}</span>
                        <span className="comparison-match">{driver.match_percentage.toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* What to Work On */}
          {prediction?.recommendations && prediction.recommendations.length > 0 && (
            <div className="recommendations-card">
              <h2>What to Work On</h2>
              <p className="recommendations-subtitle">
                Based on your weakest skills, here's where to focus your practice:
              </p>

              <div className="recommendations-list">
                {prediction.recommendations.slice(0, 2).map((rec, idx) => (
                  <div key={idx} className="recommendation-item">
                    <div className="recommendation-header">
                      <div className="recommendation-priority">{rec.priority}</div>
                      <div className="recommendation-title">
                        <h3>{rec.display_name}</h3>
                        <p className="recommendation-current">
                          Current: {rec.current_percentile.toFixed(0)}th percentile
                        </p>
                      </div>
                    </div>

                    <div className="recommendation-focus">
                      <h4>Primary Focus:</h4>
                      <p>{rec.rationale}</p>
                    </div>

                    {rec.drills && rec.drills.length > 0 && (
                      <div className="recommendation-drills">
                        <h4>Recommended Drills:</h4>
                        <ul>
                          {rec.drills.slice(0, 3).map((drill, dIdx) => (
                            <li key={dIdx}>{drill}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="recommendation-impact">
                      {rec.impact_estimate}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Updating overlay */}
      {updating && (
        <div className="updating-overlay">
          <div className="updating-spinner"></div>
        </div>
      )}
    </div>
  );
}
