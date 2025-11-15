export default function FlagIcon({ size = 'md', className = '' }) {
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
      className={`flag-icon ${className}`}
      aria-label="Checkered flag icon"
    >
      {/* Flag pole */}
      <rect x="8" y="8" width="4" height="52" fill="#1a1a1a" rx="2" />

      {/* Checkered flag pattern */}
      <g>
        {/* Row 1 */}
        <rect x="12" y="8" width="8" height="6" fill="#1a1a1a" />
        <rect x="20" y="8" width="8" height="6" fill="white" />
        <rect x="28" y="8" width="8" height="6" fill="#1a1a1a" />
        <rect x="36" y="8" width="8" height="6" fill="white" />
        <rect x="44" y="8" width="8" height="6" fill="#1a1a1a" />

        {/* Row 2 */}
        <rect x="12" y="14" width="8" height="6" fill="white" />
        <rect x="20" y="14" width="8" height="6" fill="#1a1a1a" />
        <rect x="28" y="14" width="8" height="6" fill="white" />
        <rect x="36" y="14" width="8" height="6" fill="#1a1a1a" />
        <rect x="44" y="14" width="8" height="6" fill="white" />

        {/* Row 3 */}
        <rect x="12" y="20" width="8" height="6" fill="#1a1a1a" />
        <rect x="20" y="20" width="8" height="6" fill="white" />
        <rect x="28" y="20" width="8" height="6" fill="#1a1a1a" />
        <rect x="36" y="20" width="8" height="6" fill="white" />
        <rect x="44" y="20" width="8" height="6" fill="#1a1a1a" />

        {/* Row 4 */}
        <rect x="12" y="26" width="8" height="6" fill="white" />
        <rect x="20" y="26" width="8" height="6" fill="#1a1a1a" />
        <rect x="28" y="26" width="8" height="6" fill="white" />
        <rect x="36" y="26" width="8" height="6" fill="#1a1a1a" />
        <rect x="44" y="26" width="8" height="6" fill="white" />
      </g>

      {/* Flag border */}
      <rect x="12" y="8" width="40" height="24" stroke="#1a1a1a" strokeWidth="1" fill="none" />
    </svg>
  );
}
