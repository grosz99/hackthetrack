/**
 * SkillSliders Component
 * Interactive sliders to set target skill levels with 1% increments
 */

import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './SkillSliders.css';

const SKILLS = [
  { key: 'speed', label: 'SPEED', icon: '' },
  { key: 'consistency', label: 'CONSISTENCY', icon: '' },
  { key: 'racecraft', label: 'RACECRAFT', icon: '' },
  { key: 'tire_management', label: 'TIRE MGMT', icon: '' }
];

export default function SkillSliders({ currentSkills, onTargetChange, onFindSimilar }) {
  // Initialize target skills to current skills (clamped to valid range)
  const getInitialTargets = () => ({
    speed: Math.min(100, Math.max(0, Math.round(currentSkills.speed || 0))),
    consistency: Math.min(100, Math.max(0, Math.round(currentSkills.consistency || 0))),
    racecraft: Math.min(100, Math.max(0, Math.round(currentSkills.racecraft || 0))),
    tire_management: Math.min(100, Math.max(0, Math.round(currentSkills.tire_management || 0)))
  });

  const [targetSkills, setTargetSkills] = useState(getInitialTargets());

  // Reset target skills when current skills change (e.g., driver changes)
  useEffect(() => {
    setTargetSkills(getInitialTargets());
  }, [currentSkills.speed, currentSkills.consistency, currentSkills.racecraft, currentSkills.tire_management]);

  // Calculate total increase across all skills
  const getTotalIncrease = (skills = targetSkills) => {
    return SKILLS.reduce((total, skill) => {
      const current = Math.round(currentSkills[skill.key] || 0);
      const target = skills[skill.key];
      return total + Math.max(0, target - current);
    }, 0);
  };

  const MAX_TOTAL_INCREASE = 5; // Maximum 5% total increase

  const handleSliderChange = (skill, value) => {
    const newValue = Math.min(100, Math.max(0, parseInt(value, 10)));
    const current = Math.round(currentSkills[skill] || 0);

    // Can't go below current value
    if (newValue < current) {
      return;
    }

    const proposedIncrease = newValue - current;

    // Calculate what the total would be with this change
    const currentGap = getGap(skill);
    const otherSkillsIncrease = getTotalIncrease() - currentGap;
    const newTotal = otherSkillsIncrease + proposedIncrease;

    // Only allow if within budget
    if (newTotal <= MAX_TOTAL_INCREASE) {
      const updated = { ...targetSkills, [skill]: newValue };
      setTargetSkills(updated);
      onTargetChange(updated);
    } else {
      // Clamp to maximum allowed value
      const availableBudget = MAX_TOTAL_INCREASE - otherSkillsIncrease;
      const maxAllowedValue = current + availableBudget;
      if (maxAllowedValue > current) {
        const updated = { ...targetSkills, [skill]: maxAllowedValue };
        setTargetSkills(updated);
        onTargetChange(updated);
      }
    }
  };

  const incrementSkill = (skill) => {
    const current = Math.round(currentSkills[skill] || 0);
    const target = targetSkills[skill];

    // Check if we have budget and haven't hit max
    if (target < 100 && getTotalIncrease() < MAX_TOTAL_INCREASE) {
      handleSliderChange(skill, target + 1);
    }
  };

  const decrementSkill = (skill) => {
    const currentValue = Math.round(currentSkills[skill] || 0);
    if (targetSkills[skill] > currentValue) {
      handleSliderChange(skill, targetSkills[skill] - 1);
    }
  };

  const getGap = (skill) => {
    const current = Math.round(currentSkills[skill] || 0);
    const target = targetSkills[skill];
    return Math.max(0, target - current);
  };

  const hasChanges = () => {
    return getTotalIncrease() > 0;
  };

  const getRemainingBudget = () => {
    return MAX_TOTAL_INCREASE - getTotalIncrease();
  };

  return (
    <div className="skill-sliders">
      <div className="sliders-header">
        <h3>Set Your Target Skills</h3>
        <p className="sliders-subtitle">You have a total budget of 5% to distribute across all skills</p>
        <div className="budget-indicator">
          <span className="budget-label">Remaining Budget:</span>
          <span className={`budget-value ${getRemainingBudget() === 0 ? 'budget-depleted' : ''}`}>
            {getRemainingBudget()}%
          </span>
        </div>
      </div>

      <div className="sliders-container">
        {SKILLS.map(({ key, label, icon }) => {
          const current = Math.round(currentSkills[key] || 0);
          const target = targetSkills[key];
          const gap = getGap(key);
          const percentage = (target / 100) * 100;

          return (
            <div key={key} className="skill-slider-row">
              <div className="skill-header">
                {icon && <span className="skill-icon">{icon}</span>}
                <span className="skill-label">{label}</span>
                <div className="skill-values">
                  <span className="current-value">{current}</span>
                  <span className="arrow">→</span>
                  <span className={`target-value ${gap > 0 ? 'has-change' : ''}`}>
                    {target}
                  </span>
                  {gap > 0 && (
                    <span className="gap-indicator">+{gap}</span>
                  )}
                </div>
              </div>

              <div className="slider-controls">
                <div className="slider-track-container">
                  <div className="slider-track">
                    <div
                      className="slider-fill"
                      style={{ width: `${percentage}%` }}
                    />
                    <div
                      className="current-marker"
                      style={{ left: `${(current / 100) * 100}%` }}
                      title={`Current: ${current}`}
                    />
                  </div>
                  <input
                    type="range"
                    min={current}
                    max={Math.min(100, current + getRemainingBudget() + getGap(key))}
                    value={target}
                    onChange={(e) => handleSliderChange(key, e.target.value)}
                    className="slider-input"
                  />
                </div>

                <div className="increment-buttons">
                  <button
                    onClick={() => decrementSkill(key)}
                    disabled={target <= current}
                    className="increment-btn decrement"
                    title="Decrease by 1%"
                  >
                    -1%
                  </button>
                  <button
                    onClick={() => incrementSkill(key)}
                    disabled={target >= 100 || getRemainingBudget() === 0}
                    className="increment-btn increment"
                    title={getRemainingBudget() === 0 ? "Budget depleted" : "Increase by 1%"}
                  >
                    +1%
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="sliders-footer">
        <button
          onClick={onFindSimilar}
          disabled={!hasChanges()}
          className="find-similar-btn"
        >
          <span>Find Similar Driver</span>
        </button>
        {!hasChanges() ? (
          <p className="helper-text">Use your {MAX_TOTAL_INCREASE}% budget to set target skills</p>
        ) : (
          <p className="helper-text">Using {getTotalIncrease()}% of your {MAX_TOTAL_INCREASE}% budget</p>
        )}
      </div>
    </div>
  );
}

SkillSliders.propTypes = {
  currentSkills: PropTypes.shape({
    speed: PropTypes.number,
    consistency: PropTypes.number,
    racecraft: PropTypes.number,
    tire_management: PropTypes.number
  }).isRequired,
  onTargetChange: PropTypes.func.isRequired,
  onFindSimilar: PropTypes.func.isRequired
};
