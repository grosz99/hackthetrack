import './ClassificationBadge.css';

/**
 * ClassificationBadge - Displays driver tier classification
 * Professional, racing-themed badge (no emojis)
 */
export default function ClassificationBadge({ classification, size = 'medium', showDescription = false }) {
  if (!classification) return null;

  const sizeClass = `badge-${size}`;

  return (
    <div className="classification-badge-container">
      <div className={`classification-badge ${sizeClass}`} style={{
        backgroundColor: classification.bgColor,
        borderColor: classification.color,
        color: classification.color
      }}>
        <span className="badge-label">{classification.label}</span>
      </div>
      {showDescription && (
        <div className="badge-description">{classification.description}</div>
      )}
    </div>
  );
}
