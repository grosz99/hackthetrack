export default function MessageIcon({ size = 'md', className = '' }) {
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
      className={`message-icon ${className}`}
      aria-label="Message icon"
    >
      {/* Speech bubble */}
      <path
        d="M8 12C8 9.79086 9.79086 8 12 8H52C54.2091 8 56 9.79086 56 12V40C56 42.2091 54.2091 44 52 44H24L12 56V44C9.79086 44 8 42.2091 8 40V12Z"
        fill="#3b82f6"
        stroke="#2563eb"
        strokeWidth="2"
      />

      {/* Message lines */}
      <line x1="16" y1="20" x2="48" y2="20" stroke="white" strokeWidth="2" strokeLinecap="round" />
      <line x1="16" y1="28" x2="40" y2="28" stroke="white" strokeWidth="2" strokeLinecap="round" />
      <line x1="16" y1="36" x2="44" y2="36" stroke="white" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
