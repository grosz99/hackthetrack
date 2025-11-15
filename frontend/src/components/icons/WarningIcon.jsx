export default function WarningIcon({ size = 'md', className = '' }) {
  const sizes = {
    sm: 20,
    md: 24,
    lg: 32,
    xl: 48
  };

  const dimension = sizes[size] || sizes.md;

  return (
    <svg
      width={dimension}
      height={dimension}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`warning-icon ${className}`}
      aria-label="Warning icon"
    >
      {/* Triangle background */}
      <path
        d="M32 8L56 52H8L32 8z"
        fill="#f59e0b"
        stroke="#d97706"
        strokeWidth="2"
      />

      {/* Exclamation mark */}
      <line x1="32" y1="22" x2="32" y2="38" stroke="white" strokeWidth="4" strokeLinecap="round" />
      <circle cx="32" cy="46" r="2.5" fill="white" />
    </svg>
  );
}
