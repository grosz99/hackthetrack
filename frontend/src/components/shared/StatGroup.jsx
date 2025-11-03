import React from 'react';
/**
 * StatGroup - Groups related stats together like StatMus player cards
 *
 * Organizes stats into logical categories with headers and consistent styling
 */

import StatCard from './StatCard';

export default function StatGroup({ title, description, stats, className = '' }) {
  return (
    <div className={`stat-group ${className}`}>
      {/* Group Header */}
      <div className="stat-group-header">
        <h3 className="stat-group-title">{title}</h3>
        {description && (
          <p className="stat-group-description">{description}</p>
        )}
      </div>

      {/* Stats Grid */}
      <div className="stat-group-grid">
        {stats.map((stat, index) => (
          <StatCard
            key={index}
            label={stat.label}
            value={stat.value}
            percentile={stat.percentile}
            visual={stat.visual}
            trend={stat.trend}
            className="stat-group-card"
          />
        ))}
      </div>
    </div>
  );
}
