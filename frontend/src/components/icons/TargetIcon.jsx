export default function TargetIcon({ size = 'md', className = '' }) {
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
      className={`target-icon ${className}`}
      aria-label="Target icon"
    >
      {/* Outer ring - White */}
      <circle cx="32" cy="32" r="28" fill="white" stroke="#EB0A1E" strokeWidth="2" />

      {/* Middle ring - Red */}
      <circle cx="32" cy="32" r="20" fill="#EB0A1E" />

      {/* Inner ring - White */}
      <circle cx="32" cy="32" r="12" fill="white" />

      {/* Center - Red */}
      <circle cx="32" cy="32" r="6" fill="#EB0A1E" />

      {/* Center dot - White */}
      <circle cx="32" cy="32" r="2" fill="white" />
    </svg>
  );
}
