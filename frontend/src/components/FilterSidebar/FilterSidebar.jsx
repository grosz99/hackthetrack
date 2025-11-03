import React from 'react';
import { useScout } from '../../context/ScoutContext';
import { CLASSIFICATIONS } from '../../utils/classification';
import './FilterSidebar.css';

export default function FilterSidebar({ resultCount }) {
  const { filters, updateFilter, resetFilters } = useScout();

  const handleClassificationChange = (classId) => {
    const current = filters.classification;
    const updated = current.includes(classId)
      ? current.filter(id => id !== classId)
      : [...current, classId];
    updateFilter('classification', updated);
  };

  const handleExperienceChange = (exp) => {
    const current = filters.experience;
    const updated = current.includes(exp)
      ? current.filter(e => e !== exp)
      : [...current, exp];
    updateFilter('experience', updated);
  };

  const handleAttributeChange = (attr) => {
    const current = filters.attributes;
    const updated = current.includes(attr)
      ? current.filter(a => a !== attr)
      : [...current, attr];
    updateFilter('attributes', updated);
  };

  return (
    <div className="filter-sidebar">
      <div className="filter-header">
        <h2>Filters</h2>
        <button className="btn-reset" onClick={resetFilters}>
          Reset All
        </button>
      </div>

      {/* Result Count */}
      <div className="result-count">
        <span className="count-number">{resultCount}</span>
        <span className="count-label">drivers found</span>
      </div>

      {/* Classification Filter */}
      <div className="filter-section">
        <h3 className="filter-title">Classification</h3>
        <div className="filter-options">
          {Object.values(CLASSIFICATIONS).map(classification => (
            <label key={classification.id} className="filter-checkbox">
              <input
                type="checkbox"
                checked={filters.classification.includes(classification.id)}
                onChange={() => handleClassificationChange(classification.id)}
              />
              <span className="checkbox-label">
                <span
                  className="color-indicator"
                  style={{ backgroundColor: classification.color }}
                ></span>
                {classification.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Experience Filter */}
      <div className="filter-section">
        <h3 className="filter-title">Experience Level</h3>
        <div className="filter-options">
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.experience.includes('VETERAN')}
              onChange={() => handleExperienceChange('VETERAN')}
            />
            <span className="checkbox-label">Veteran (10+ races)</span>
          </label>
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.experience.includes('DEVELOPING')}
              onChange={() => handleExperienceChange('DEVELOPING')}
            />
            <span className="checkbox-label">Developing (5-9 races)</span>
          </label>
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.experience.includes('ROOKIE')}
              onChange={() => handleExperienceChange('ROOKIE')}
            />
            <span className="checkbox-label">Rookie (&lt;5 races)</span>
          </label>
        </div>
      </div>

      {/* Attribute Filter */}
      <div className="filter-section">
        <h3 className="filter-title">Performance Attributes</h3>
        <div className="filter-options">
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.attributes.includes('SPEED')}
              onChange={() => handleAttributeChange('SPEED')}
            />
            <span className="checkbox-label">Speed Specialist (70+)</span>
          </label>
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.attributes.includes('WHEEL_TO_WHEEL')}
              onChange={() => handleAttributeChange('WHEEL_TO_WHEEL')}
            />
            <span className="checkbox-label">Wheel-to-Wheel (60+)</span>
          </label>
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.attributes.includes('CONSISTENT')}
              onChange={() => handleAttributeChange('CONSISTENT')}
            />
            <span className="checkbox-label">Consistency Driver (60+)</span>
          </label>
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.attributes.includes('HIGH_UPSIDE')}
              onChange={() => handleAttributeChange('HIGH_UPSIDE')}
            />
            <span className="checkbox-label">High Upside</span>
          </label>
        </div>
      </div>

      {/* Range Filters */}
      <div className="filter-section">
        <h3 className="filter-title">Metric Ranges</h3>

        <div className="range-filter">
          <label className="range-label">
            Overall Score: {filters.overallRange[0]} - {filters.overallRange[1]}
          </label>
          <div className="range-inputs">
            <input
              type="range"
              min="30"
              max="70"
              value={filters.overallRange[0]}
              onChange={(e) => updateFilter('overallRange', [Number(e.target.value), filters.overallRange[1]])}
            />
            <input
              type="range"
              min="30"
              max="70"
              value={filters.overallRange[1]}
              onChange={(e) => updateFilter('overallRange', [filters.overallRange[0], Number(e.target.value)])}
            />
          </div>
        </div>

        <div className="range-filter">
          <label className="range-label">
            Speed Percentile: {filters.speedRange[0]} - {filters.speedRange[1]}
          </label>
          <div className="range-inputs">
            <input
              type="range"
              min="0"
              max="100"
              value={filters.speedRange[0]}
              onChange={(e) => updateFilter('speedRange', [Number(e.target.value), filters.speedRange[1]])}
            />
            <input
              type="range"
              min="0"
              max="100"
              value={filters.speedRange[1]}
              onChange={(e) => updateFilter('speedRange', [filters.speedRange[0], Number(e.target.value)])}
            />
          </div>
        </div>

        <div className="range-filter">
          <label className="range-label">
            Race Experience: {filters.racesRange[0]} - {filters.racesRange[1]}
          </label>
          <div className="range-inputs">
            <input
              type="range"
              min="0"
              max="15"
              value={filters.racesRange[0]}
              onChange={(e) => updateFilter('racesRange', [Number(e.target.value), filters.racesRange[1]])}
            />
            <input
              type="range"
              min="0"
              max="15"
              value={filters.racesRange[1]}
              onChange={(e) => updateFilter('racesRange', [filters.racesRange[0], Number(e.target.value)])}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
