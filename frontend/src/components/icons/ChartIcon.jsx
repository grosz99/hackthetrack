export default function ChartIcon({ size = 'md', className = '' }) {
  const sizes = {
    sm: 20,
    md: 32,
    lg: 48,
    xl: 64
  };

  const dimension = sizes[size] || sizes.md;

  return (
    <svg
      width={dimension}
      height={dimension}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`chart-icon ${className}`}
      aria-label="Chart icon"
    >
      {/* Chart bars */}
      <rect x="8" y="40" width="10" height="16" rx="2" fill="#3b82f6" />
      <rect x="22" y="28" width="10" height="28" rx="2" fill="#3b82f6" />
      <rect x="36" y="20" width="10" height="36" rx="2" fill="#3b82f6" />
      <rect x="50" y="32" width="10" height="24" rx="2" fill="#3b82f6" />

      {/* Base line */}
      <line x1="4" y1="58" x2="60" y2="58" stroke="#1a1a1a" strokeWidth="2" />
    </svg>
  );
}
