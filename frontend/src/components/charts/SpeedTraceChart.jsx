import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceArea
} from 'recharts';
import './SpeedTraceChart.css';

/**
 * SpeedTraceChart - Three-tier speed comparison visualization
 *
 * Shows speed traces for:
 * - User (red): Your performance
 * - Next Tier (orange): Driver 1-2 positions ahead (achievable target)
 * - Leader (green): Race winner (ultimate goal)
 * - Highlighted corners: Specific corners mentioned by AI coach
 */
const SpeedTraceChart = ({ telemetryData, comparisonDrivers, highlightedCorners = [] }) => {
  if (!telemetryData || !telemetryData.traces) {
    return (
      <div className="speed-trace-empty">
        <p>No telemetry data available</p>
      </div>
    );
  }

  const { traces } = telemetryData;

  // Estimate corner positions (simplified - assumes 17 corners at Barber)
  const totalCorners = 17; // This could be made track-specific
  const estimateCornerPosition = (cornerNumber) => {
    const lapLength = Math.max(
      traces.user?.distance?.length || 0,
      traces.next_tier?.distance?.length || 0,
      traces.leader?.distance?.length || 0
    );

    // Estimate corner position as a percentage of lap
    const cornerPercentage = (cornerNumber - 0.5) / totalCorners; // Center of the corner
    const position = Math.floor(cornerPercentage * lapLength);

    // Return a range (±5% of lap for the corner zone)
    const rangeSize = Math.floor(lapLength * 0.05);
    return {
      start: Math.max(0, position - rangeSize),
      end: Math.min(lapLength - 1, position + rangeSize),
      label: `T${cornerNumber}`
    };
  };

  // Transform data for recharts format
  const chartData = [];
  const maxLength = Math.max(
    traces.user?.distance?.length || 0,
    traces.next_tier?.distance?.length || 0,
    traces.leader?.distance?.length || 0
  );

  for (let i = 0; i < maxLength; i++) {
    const dataPoint = { distance: i };

    if (traces.user?.speed?.[i] !== undefined) {
      dataPoint.yourSpeed = traces.user.speed[i];
    }

    if (traces.next_tier?.speed?.[i] !== undefined) {
      dataPoint.nextTierSpeed = traces.next_tier.speed[i];
    }

    if (traces.leader?.speed?.[i] !== undefined &&
        traces.leader.driver_number !== traces.user?.driver_number) {
      dataPoint.leaderSpeed = traces.leader.speed[i];
    }

    chartData.push(dataPoint);
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{`Distance Point: ${payload[0].payload.distance}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value?.toFixed(1)} mph`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="speed-trace-container">
      <div className="speed-trace-header">
        <h3>Speed Trace Comparison</h3>
        <div className="speed-trace-legend-custom">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#EB0A1E' }}></div>
            <span>You (#{traces.user?.driver_number})</span>
          </div>
          {traces.next_tier && (
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#FF9500' }}></div>
              <span>Next Tier (#{traces.next_tier.driver_number}) - P{comparisonDrivers?.user_position - 1}</span>
            </div>
          )}
          {traces.leader && traces.leader.driver_number !== traces.user?.driver_number && (
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#34C759' }}></div>
              <span>Leader (#{traces.leader.driver_number}) - P1</span>
            </div>
          )}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e7" />
          <XAxis
            dataKey="distance"
            label={{ value: 'Distance Around Lap', position: 'insideBottom', offset: -10 }}
            stroke="#86868b"
          />
          <YAxis
            label={{ value: 'Speed (mph)', angle: -90, position: 'insideLeft' }}
            stroke="#86868b"
            domain={['dataMin - 5', 'dataMax + 5']}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Highlighted corner regions */}
          {highlightedCorners.map(cornerNum => {
            const corner = estimateCornerPosition(cornerNum);
            return (
              <ReferenceArea
                key={cornerNum}
                x1={corner.start}
                x2={corner.end}
                fill="#FFD700"
                fillOpacity={0.2}
                stroke="#FFD700"
                strokeOpacity={0.6}
                strokeWidth={2}
                label={{
                  value: corner.label,
                  position: 'insideTop',
                  fill: '#1d1d1f',
                  fontWeight: 'bold',
                  fontSize: 12
                }}
              />
            );
          })}

          {/* Your speed trace - RED */}
          <Line
            type="monotone"
            dataKey="yourSpeed"
            stroke="#EB0A1E"
            strokeWidth={3}
            dot={false}
            name="You"
            connectNulls
          />

          {/* Next tier speed trace - ORANGE */}
          {traces.next_tier && (
            <Line
              type="monotone"
              dataKey="nextTierSpeed"
              stroke="#FF9500"
              strokeWidth={2.5}
              dot={false}
              name="Next Tier"
              connectNulls
            />
          )}

          {/* Leader speed trace - GREEN */}
          {traces.leader && traces.leader.driver_number !== traces.user?.driver_number && (
            <Line
              type="monotone"
              dataKey="leaderSpeed"
              stroke="#34C759"
              strokeWidth={2}
              dot={false}
              name="Leader"
              connectNulls
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      <div className="speed-trace-insights">
        <h4>Key Insights</h4>
        <ul>
          <li>🔴 <strong>Red line (You):</strong> Your current speed profile</li>
          {traces.next_tier && (
            <li>🟠 <strong>Orange line (Next Tier):</strong> Achievable target - driver just ahead of you</li>
          )}
          {traces.leader && traces.leader.driver_number !== traces.user?.driver_number && (
            <li>🟢 <strong>Green line (Leader):</strong> Ultimate goal - race winner's pace</li>
          )}
          {highlightedCorners.length > 0 && (
            <li>⭐ <strong>Highlighted zones (Gold):</strong> {highlightedCorners.map(c => `Turn ${c}`).join(', ')} - Focus areas mentioned by your coach</li>
          )}
          <li>📊 <strong>Look for gaps:</strong> Where lines diverge shows opportunities for improvement</li>
        </ul>
      </div>
    </div>
  );
};

export default SpeedTraceChart;
