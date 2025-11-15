export default function RocketIcon({ size = 'md', className = '' }) {
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
      className={`rocket-icon ${className}`}
      aria-label="Rocket icon"
    >
      {/* Rocket body */}
      <path
        d="M32 4C32 4 24 12 24 28V44L28 52L32 56L36 52L40 44V28C40 12 32 4 32 4Z"
        fill="#e74c3c"
        stroke="#c0392b"
        strokeWidth="2"
      />

      {/* Window */}
      <circle cx="32" cy="22" r="6" fill="#3b82f6" stroke="#2563eb" strokeWidth="2" />

      {/* Left fin */}
      <path
        d="M24 40L16 48L20 52L24 44Z"
        fill="#c0392b"
        stroke="#a93226"
        strokeWidth="2"
      />

      {/* Right fin */}
      <path
        d="M40 40L48 48L44 52L40 44Z"
        fill="#c0392b"
        stroke="#a93226"
        strokeWidth="2"
      />

      {/* Flame */}
      <path
        d="M28 52C28 54 30 58 32 60C34 58 36 54 36 52"
        fill="#f39c12"
        stroke="#e67e22"
        strokeWidth="2"
      />
    </svg>
  );
}
