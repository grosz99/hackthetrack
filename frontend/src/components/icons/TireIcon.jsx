export default function TireIcon({ size = 'md', className = '' }) {
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
      className={`tire-icon ${className}`}
      aria-label="Tire icon"
    >
      {/* Outer tire */}
      <circle cx="32" cy="32" r="26" fill="#2c3e50" stroke="#1a252f" strokeWidth="2" />

      {/* Inner rim */}
      <circle cx="32" cy="32" r="18" fill="#34495e" stroke="#2c3e50" strokeWidth="2" />

      {/* Center hub */}
      <circle cx="32" cy="32" r="8" fill="#7f8c8d" stroke="#5d6d7e" strokeWidth="2" />

      {/* Tread pattern lines */}
      <path d="M32 6 L32 10" stroke="#1a252f" strokeWidth="3" strokeLinecap="round" />
      <path d="M32 54 L32 58" stroke="#1a252f" strokeWidth="3" strokeLinecap="round" />
      <path d="M6 32 L10 32" stroke="#1a252f" strokeWidth="3" strokeLinecap="round" />
      <path d="M54 32 L58 32" stroke="#1a252f" strokeWidth="3" strokeLinecap="round" />
      <path d="M13 13 L16 16" stroke="#1a252f" strokeWidth="3" strokeLinecap="round" />
      <path d="M48 48 L51 51" stroke="#1a252f" strokeWidth="3" strokeLinecap="round" />
      <path d="M51 13 L48 16" stroke="#1a252f" strokeWidth="3" strokeLinecap="round" />
      <path d="M16 48 L13 51" stroke="#1a252f" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
