import React from 'react';
import { useNavigate } from 'react-router-dom';
import ClassificationBadge from '../ClassificationBadge/ClassificationBadge';
import { classifyDriver, getDriverTags, getDataConfidence } from '../../utils/classification';
import { useScout } from '../../context/ScoutContext';
import './DriverCard.css';

export default function DriverCard({ driver }) {
  const navigate = useNavigate();
  const { addToComparison, comparisonQueue, toggleDriverSelection, selectedDrivers } = useScout();

  const classification = classifyDriver(driver);
  const tags = getDriverTags(driver);
  const confidence = getDataConfidence(driver.races);
  const isSelected = selectedDrivers.includes(driver.number);
  const isInComparison = comparisonQueue.includes(driver.number);

  const handleViewDetails = () => {
    navigate(`/scout/driver/${driver.number}/overview`);
  };

  const handleCompare = (e) => {
    e.stopPropagation();
    addToComparison(driver.number);
  };

  const handleCheckbox = (e) => {
    e.stopPropagation();
    toggleDriverSelection(driver.number);
  };

  return (
    <div className={`driver-card ${isSelected ? 'selected' : ''}`}>
      {/* Header */}
      <div className="card-header">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={handleCheckbox}
          className="card-checkbox"
        />
        <ClassificationBadge classification={classification} size="medium" />
        <div className="driver-number">#{driver.number}</div>
      </div>

      {/* Driver Identity */}
      <div className="driver-identity">
        <h3 className="driver-name" style={{ color: '#000000' }}>{driver.name}</h3>
        <div className="driver-tags">
          {tags.slice(0, 3).map((tag, idx) => (
            <span key={idx} className="tag">
              {tag.icon && <span className="tag-icon">{tag.icon}</span>}
              {tag.label}
            </span>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="key-metrics">
        <div className="metric-row">
          <span className="metric-label">Overall</span>
          <div className="metric-bar-container">
            <div className="metric-bar" style={{ width: `${driver.overall_score}%` }}></div>
          </div>
          <span className="metric-value">{Math.round(driver.overall_score)}</span>
        </div>
        <div className="metric-row highlight">
          <span className="metric-label">Speed</span>
          <div className="metric-bar-container">
            <div className="metric-bar" style={{ width: `${driver.factors.raw_speed.percentile}%` }}></div>
          </div>
          <span className="metric-value">{Math.round(driver.factors.raw_speed.percentile)}</span>
        </div>
        <div className="metric-row">
          <span className="metric-label">Consistency</span>
          <div className="metric-bar-container">
            <div className="metric-bar" style={{ width: `${driver.factors.consistency.percentile}%` }}></div>
          </div>
          <span className="metric-value">{Math.round(driver.factors.consistency.percentile)}</span>
        </div>
        <div className="metric-row">
          <span className="metric-label">Racecraft</span>
          <div className="metric-bar-container">
            <div className="metric-bar" style={{ width: `${driver.factors.racecraft.percentile}%` }}></div>
          </div>
          <span className="metric-value">{Math.round(driver.factors.racecraft.percentile)}</span>
        </div>
      </div>

      {/* Experience & Results */}
      <div className="driver-stats">
        <div className="stat-item">
          <span className="stat-value">{driver.races}</span>
          <span className="stat-label">Races</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{driver.avg_finish.toFixed(1)}</span>
          <span className="stat-label">Avg Finish</span>
        </div>
      </div>

      {/* Circuit Fit Summary - Optional */}
      {driver.best_tracks && driver.best_tracks.length > 0 && (
        <div className="circuit-fit">
          <div className="fit-label">Best Track:</div>
          <div className="fit-value">{driver.best_tracks[0].toUpperCase()}</div>
        </div>
      )}

      {/* Data Caveat */}
      {confidence.showWarning && (
        <div className="data-caveat" style={{ borderColor: confidence.color }}>
          <span className="caveat-icon">⚠️</span>
          <span className="caveat-text">{confidence.message}</span>
        </div>
      )}

      {/* Actions */}
      <div className="card-actions">
        <button className="btn-primary" onClick={handleViewDetails}>
          View Details
        </button>
      </div>
    </div>
  );
}
