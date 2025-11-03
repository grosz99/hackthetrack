import React from 'react';
/**
 * StatCard - PFF-style stat display card
 *
 * Large impactful numbers with labels and optional percentile badges
 */

import PercentileBadge from './PercentileBadge';

export default function StatCard({
  label,
  value,
  percentile = null,
  visual = null,
  trend = null,
  className = ''
}) {
  const getTrendIcon = (direction) => {
    if (direction === 'up') return '↑';
    if (direction === 'down') return '↓';
    return '→';
  };

  const getTrendClass = (direction) => {
    if (direction === 'up') return 'position-up';
    if (direction === 'down') return 'position-down';
    return 'position-same';
  };

  return (
    <div className={`card ${className}`}>
      {/* Label */}
      <div className="stat-label mb-3">
        {label}
      </div>

      {/* Value and Visual */}
      <div className="flex items-end justify-between">
        <div className="flex-1">
          <div className="stat-number mb-2">
            {value}
          </div>

          {/* Percentile Badge */}
          {percentile !== null && (
            <div className="mt-2">
              <PercentileBadge value={percentile} />
            </div>
          )}
        </div>

        {/* Optional Visual (icons, mini charts, etc) */}
        {visual && (
          <div className="ml-4 flex-shrink-0">
            {visual}
          </div>
        )}
      </div>

      {/* Trend Indicator */}
      {trend && (
        <div className={`mt-3 text-sm font-semibold ${getTrendClass(trend)}`}>
          {getTrendIcon(trend)} {trend === 'up' ? 'Improving' : trend === 'down' ? 'Declining' : 'Stable'}
        </div>
      )}
    </div>
  );
}
