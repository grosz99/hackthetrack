/**
 * Practice Plan Generator - THE KILLER FEATURE
 * Generates personalized week-by-week practice plans with position predictions
 */

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { TargetIcon, RocketIcon, WarningIcon, ChartIcon, FlagIcon } from '../../../components/icons';
import './PracticePlanGenerator.css';

export default function PracticePlanGenerator({ driverData, api }) {
  const [targetPosition, setTargetPosition] = useState(5);
  const [selectedTrack, setSelectedTrack] = useState('barber');
  const [weeksAvailable, setWeeksAvailable] = useState(4);
  const [practicePlan, setPracticePlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  const tracks = [
    { id: 'barber', name: 'Barber Motorsports Park', location: 'Alabama' },
    { id: 'cota', name: 'Circuit of the Americas', location: 'Texas' },
    { id: 'roadamerica', name: 'Road America', location: 'Wisconsin' },
    { id: 'sebring', name: 'Sebring International', location: 'Florida' },
    { id: 'sonoma', name: 'Sonoma Raceway', location: 'California' },
    { id: 'vir', name: 'Virginia International Raceway', location: 'Virginia' }
  ];

  // Calculate current predicted position from driver stats
  const currentPosition = driverData?.stats?.average_finish || 10;

  const handleGeneratePlan = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.post('/api/practice/generate-plan', {
        driver_number: driverData.driver_number,
        target_position: targetPosition,
        current_track: selectedTrack,
        weeks_available: weeksAvailable
      });

      setPracticePlan(response.data);
      setExpanded(true);
    } catch (err) {
      console.error('Error generating practice plan:', err);
      setError(err.response?.data?.detail || 'Failed to generate practice plan');
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const chartData = practicePlan?.weekly_plan ? [
    { week: 0, position: practicePlan.current_position, label: 'Now' },
    ...practicePlan.weekly_plan.map(week => ({
      week: week.week,
      position: week.expected_position_after_week,
      label: `Week ${week.week}`,
      focusSkill: week.focus_skill
    }))
  ] : [];

  return (
    <section className="practice-plan-generator">
      <div className="practice-plan-header">
        <div className="header-content">
          <h2><TargetIcon size="sm" className="inline-icon" /> Create Your Practice Plan</h2>
          <p>Get a personalized week-by-week plan to reach your target position</p>
        </div>
        <button
          className={`expand-btn ${expanded ? 'expanded' : ''}`}
          onClick={() => setExpanded(!expanded)}
          aria-label={expanded ? 'Collapse practice plan' : 'Expand practice plan'}
        >
          {expanded ? '▼ Collapse' : '▶ Expand'}
        </button>
      </div>

      {expanded && (
        <>
          {/* Goal Setting Section */}
          <div className="goal-setting-section">
            <div className="goal-inputs-grid">
              {/* Current Position Display */}
              <div className="goal-input">
                <label>Current Avg Position</label>
                <div className="current-position-display">
                  P{currentPosition.toFixed(1)}
                </div>
              </div>

              {/* Target Position Slider */}
              <div className="goal-input">
                <label>Target Position</label>
                <div className="slider-container">
                  <input
                    type="range"
                    min="1"
                    max="20"
                    value={targetPosition}
                    onChange={(e) => setTargetPosition(Number(e.target.value))}
                    className="position-slider"
                  />
                  <div className="slider-value">P{targetPosition}</div>
                </div>
                <div className="positions-to-gain">
                  {currentPosition > targetPosition ? (
                    <span className="gain-positive">
                      ↑ Gain {(currentPosition - targetPosition).toFixed(1)} positions
                    </span>
                  ) : (
                    <span className="gain-neutral">Already at or above target</span>
                  )}
                </div>
              </div>

              {/* Track Selector */}
              <div className="goal-input">
                <label>Track</label>
                <select
                  value={selectedTrack}
                  onChange={(e) => setSelectedTrack(e.target.value)}
                  className="track-selector"
                >
                  {tracks.map(track => (
                    <option key={track.id} value={track.id}>
                      {track.name} - {track.location}
                    </option>
                  ))}
                </select>
              </div>

              {/* Weeks Available */}
              <div className="goal-input">
                <label>Practice Timeline</label>
                <div className="slider-container">
                  <input
                    type="range"
                    min="1"
                    max="12"
                    value={weeksAvailable}
                    onChange={(e) => setWeeksAvailable(Number(e.target.value))}
                    className="weeks-slider"
                  />
                  <div className="slider-value">{weeksAvailable} weeks</div>
                </div>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGeneratePlan}
              disabled={loading || currentPosition <= targetPosition}
              className="generate-btn"
            >
              {loading ? 'Generating Plan...' : <><RocketIcon size="sm" className="btn-icon" /> Generate My Practice Plan</>}
            </button>

            {error && (
              <div className="error-message">
                <WarningIcon size="sm" className="inline-icon" /> {error}
              </div>
            )}
          </div>

          {/* Practice Plan Results */}
          {practicePlan && (
            <div className="practice-plan-results">
              {/* Success Probability */}
              <div className="success-banner">
                <div className="success-icon">
                  {practicePlan.success_probability > 0.75 ? <TargetIcon size="sm" /> : practicePlan.success_probability > 0.5 ? <ChartIcon size="sm" /> : <WarningIcon size="sm" />}
                </div>
                <div className="success-content">
                  <h3>
                    {Math.round(practicePlan.success_probability * 100)}% Success Probability
                  </h3>
                  <p>{practicePlan.ai_coaching_summary}</p>
                </div>
              </div>

              {/* Timeline Chart */}
              <div className="timeline-chart-section">
                <h3><ChartIcon size="sm" className="inline-icon" /> Your Position Progression</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="positionGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#EB0A1E" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#EB0A1E" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis
                      dataKey="label"
                      stroke="#fff"
                      style={{ fontSize: '12px' }}
                    />
                    <YAxis
                      stroke="#fff"
                      reversed
                      domain={[1, 20]}
                      style={{ fontSize: '12px' }}
                      label={{ value: 'Position', angle: -90, position: 'insideLeft', fill: '#fff' }}
                    />
                    <Tooltip
                      contentStyle={{
                        background: '#1a1a1a',
                        border: '2px solid #EB0A1E',
                        borderRadius: '8px'
                      }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="position"
                      stroke="#EB0A1E"
                      strokeWidth={3}
                      fill="url(#positionGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
                <div className="chart-legend">
                  <div className="legend-item">
                    <div className="legend-dot current"></div>
                    <span>Current: P{practicePlan.current_position}</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-dot target"></div>
                    <span>Target: P{practicePlan.target_position}</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-dot predicted"></div>
                    <span>Predicted: P{practicePlan.final_prediction.predicted_position}</span>
                  </div>
                </div>
              </div>

              {/* Skill Priorities */}
              <div className="skill-priorities-section">
                <h3><TargetIcon size="sm" className="inline-icon" /> Focus Areas (Prioritized by Impact)</h3>
                <div className="skill-priorities-grid">
                  {Object.entries(practicePlan.skill_priorities).map(([skillKey, skill]) => (
                    <div key={skillKey} className="skill-priority-card">
                      <div className="skill-header">
                        <h4>{skill.skill_name}</h4>
                        <div className="position-impact">{skill.position_impact}</div>
                      </div>
                      <div className="skill-progress">
                        <div className="progress-bar-track">
                          <div
                            className="progress-bar-fill current"
                            style={{ width: `${skill.current}%` }}
                          />
                          <div
                            className="progress-bar-fill target"
                            style={{ width: `${skill.target}%` }}
                          />
                        </div>
                        <div className="progress-labels">
                          <span>Current: {skill.current}</span>
                          <span>Target: {skill.target}</span>
                        </div>
                      </div>
                      <div className="skill-effort">
                        Effort: {skill.effort_score}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Weekly Breakdown */}
              <div className="weekly-breakdown-section">
                <h3>📅 Week-by-Week Plan</h3>
                <div className="weekly-plan-grid">
                  {practicePlan.weekly_plan.map((week) => (
                    <div key={week.week} className="week-card">
                      <div className="week-header">
                        <div className="week-number">Week {week.week}</div>
                        <div className="week-position">→ P{week.expected_position_after_week}</div>
                      </div>
                      <div className="week-focus">
                        <strong>Focus:</strong> {week.focus_skill}
                      </div>
                      <div className="week-target">
                        {week.current_score} → {week.target_score} ({week.improvement_needed})
                      </div>
                      <div className="week-drills">
                        <strong>Drills ({week.practice_hours} hrs/week):</strong>
                        <ul>
                          {week.drills.map((drill, i) => (
                            <li key={i}>{drill}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="week-milestone">
                        ✓ {week.milestone}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Final Prediction */}
              <div className="final-prediction-section">
                <h3><FlagIcon size="sm" className="inline-icon" /> Final Prediction</h3>
                <div className="prediction-stats">
                  <div className="prediction-stat">
                    <div className="stat-label">Predicted Final Position</div>
                    <div className="stat-value">
                      P{practicePlan.final_prediction.predicted_position}
                    </div>
                  </div>
                  <div className="prediction-stat">
                    <div className="stat-label">Confidence Interval</div>
                    <div className="stat-value">
                      P{practicePlan.final_prediction.confidence_interval[0]} - P{practicePlan.final_prediction.confidence_interval[1]}
                    </div>
                  </div>
                  <div className="prediction-stat">
                    <div className="stat-label">Success Probability</div>
                    <div className="stat-value">
                      {Math.round(practicePlan.final_prediction.success_probability * 100)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
