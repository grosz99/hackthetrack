/**
 * Performance Analysis Component
 * Shows telemetry coaching insights with corner-by-corner comparison
 * Scalable for all tracks (currently showing Barber R1)
 */

import './PerformanceAnalysis.css';

export default function PerformanceAnalysis({ coachingData, driverData }) {
  if (!coachingData) {
    return (
      <section className="performance-section">
        <div className="section-header">
          <h2>PERFORMANCE ANALYSIS</h2>
          <p className="section-subtitle">Focus areas for maximum improvement</p>
        </div>
        <div className="error-message">No coaching data available</div>
      </section>
    );
  }

  const { summary, key_insights, factor_breakdown, detailed_comparisons } = coachingData;

  // Calculate priority areas from factor breakdown
  const priorityAreas = Object.entries(factor_breakdown || {})
    .map(([factor, count]) => ({
      name: factor,
      issues: count,
      percentage: Math.round((count / summary.total_corners) * 100)
    }))
    .sort((a, b) => b.issues - a.issues);

  // Get top strengths from driver data
  const getTopStrengths = () => {
    if (!driverData) return [];

    const factors = [
      { name: 'Speed', value: driverData.speed?.score || 0 },
      { name: 'Consistency', value: driverData.consistency?.score || 0 },
      { name: 'Racecraft', value: driverData.racecraft?.score || 0 },
      { name: 'Tire Management', value: driverData.tire_management?.score || 0 }
    ];

    return factors
      .filter(f => f.value >= 70)
      .sort((a, b) => b.value - a.value)
      .slice(0, 2);
  };

  const topStrengths = getTopStrengths();

  return (
    <section className="performance-section">
      <div className="section-header">
        <h2>PERFORMANCE ANALYSIS</h2>
        <p className="section-subtitle">Barber Motorsports Park - Race 1</p>
      </div>

      {/* Team Principal's Note */}
      <div className="team-note">
        <div className="note-icon">💬</div>
        <div className="note-content">
          <h3>Team Principal's Assessment</h3>
          <p>
            {summary.primary_weakness ?
              `Focus on ${summary.primary_weakness} - you're ${summary.corners_need_work}/${summary.total_corners} corners off pace at Barber.` :
              "Strong performance! Keep refining your technique to stay competitive."
            }
          </p>
          <div className="pace-summary">
            <div className="pace-stat">
              <span className="stat-label">On Pace</span>
              <span className="stat-value good">{summary.corners_on_pace}/{summary.total_corners}</span>
            </div>
            <div className="pace-stat">
              <span className="stat-label">Need Work</span>
              <span className="stat-value needs-work">{summary.corners_need_work}/{summary.total_corners}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Insights */}
      {key_insights && key_insights.length > 0 && (
        <div className="key-insights">
          <h3>🎯 KEY FOCUS AREAS</h3>
          <div className="insights-list">
            {key_insights.map((insight, index) => (
              <div key={index} className="insight-item">
                <div className="insight-number">{index + 1}</div>
                <div className="insight-text">{insight}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Priority Areas by Factor */}
      {priorityAreas.length > 0 && (
        <div className="priority-areas">
          <h3>PRIORITY AREAS BY SKILL</h3>
          {priorityAreas.map(area => (
            <div key={area.name} className="priority-item">
              <div className="priority-header">
                <span className="priority-name">{area.name}</span>
                <span className="priority-count">{area.issues} corners need work</span>
              </div>
              <div className="priority-bar">
                <div
                  className="priority-fill"
                  style={{ width: `${area.percentage}%` }}
                ></div>
              </div>
              <div className="priority-text">
                {area.percentage}% of corners affected
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Corner-by-Corner Breakdown */}
      {detailed_comparisons && detailed_comparisons.length > 0 && (
        <div className="corner-breakdown">
          <h3>CORNER-BY-CORNER ANALYSIS</h3>
          <p className="breakdown-subtitle">Compared to fastest driver at Barber</p>
          <div className="corners-grid">
            {detailed_comparisons.map((corner, index) => {
              const isOnPace = Math.abs(corner.speed_delta_mph) < 1;
              const isSlower = corner.speed_delta_mph < 0;

              return (
                <div key={index} className={`corner-card ${isOnPace ? 'on-pace' : isSlower ? 'slower' : 'faster'}`}>
                  <div className="corner-header">
                    <h4>Turn {corner.corner_num}</h4>
                    <span className="corner-factor">{corner.factor}</span>
                  </div>

                  <div className="corner-metrics">
                    <div className="metric">
                      <span className="metric-label">Speed Δ</span>
                      <span className={`metric-value ${isSlower ? 'negative' : 'positive'}`}>
                        {corner.speed_delta_mph > 0 ? '+' : ''}{corner.speed_delta_mph.toFixed(1)} mph
                      </span>
                    </div>
                    {corner.brake_delta_m !== 0 && (
                      <div className="metric">
                        <span className="metric-label">Brake Δ</span>
                        <span className="metric-value">
                          {corner.brake_delta_m > 0 ? `${corner.brake_delta_m}m earlier` : `${Math.abs(corner.brake_delta_m)}m later`}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="corner-insight">
                    {corner.insight}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Top Strengths */}
      {topStrengths.length > 0 && (
        <div className="top-strengths">
          <h3>✨ YOUR STRENGTHS</h3>
          <div className="strengths-grid">
            {topStrengths.map(strength => (
              <div key={strength.name} className="strength-item">
                <span className="strength-name">{strength.name}</span>
                <span className="strength-score">{Math.round(strength.value)}/100</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Future Tracks Notice */}
      <div className="future-tracks-notice">
        <p>🏁 More tracks coming soon: Sebring, COTA, Sonoma, Road America, VIR</p>
      </div>
    </section>
  );
}
