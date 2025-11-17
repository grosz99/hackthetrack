export default function SwordIcon({ size = 'md', className = '' }) {
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
      className={`sword-icon ${className}`}
      aria-label="Crossed swords icon"
    >
      {/* Left sword */}
      <g>
        <rect x="8" y="28" width="48" height="8" fill="#7f8c8d" stroke="#5d6d7e" strokeWidth="2" transform="rotate(-45 32 32)" />
        <rect x="6" y="50" width="8" height="8" fill="#34495e" stroke="#2c3e50" strokeWidth="2" />
      </g>

      {/* Right sword */}
      <g>
        <rect x="8" y="28" width="48" height="8" fill="#7f8c8d" stroke="#5d6d7e" strokeWidth="2" transform="rotate(45 32 32)" />
        <rect x="50" y="50" width="8" height="8" fill="#34495e" stroke="#2c3e50" strokeWidth="2" />
      </g>

      {/* Center circle */}
      <circle cx="32" cy="32" r="6" fill="#EB0A1E" stroke="#B80818" strokeWidth="2" />
    </svg>
  );
}
