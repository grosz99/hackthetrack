/**
 * PercentileBadge - Color-coded percentile indicator (PFF Style)
 *
 * Shows percentile with color coding:
 * - Elite (90+): Bright green
 * - Great (70-89): Neon green
 * - Good (50-69): Gold
 * - Average (30-49): Orange
 * - Poor (<30): Red
 */

export default function PercentileBadge({ value, showLabel = true, className = '' }) {
  const getColorClass = (percentile) => {
    if (percentile >= 90) return 'badge-elite';
    if (percentile >= 70) return 'badge-great';
    if (percentile >= 50) return 'badge-good';
    if (percentile >= 30) return 'badge-average';
    return 'badge-poor';
  };

  const getLabel = (percentile) => {
    if (percentile >= 90) return 'ELITE';
    if (percentile >= 70) return 'GREAT';
    if (percentile >= 50) return 'GOOD';
    if (percentile >= 30) return 'AVG';
    return 'POOR';
  };

  const colorClass = getColorClass(value);
  const label = getLabel(value);

  return (
    <span className={`badge ${colorClass} ${className}`}>
      {showLabel ? `${label} (${value}%)` : `${value}%`}
    </span>
  );
}
