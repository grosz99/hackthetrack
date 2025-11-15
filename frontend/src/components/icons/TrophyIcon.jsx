export default function TrophyIcon({ size = 'md', className = '' }) {
  const sizes = {
    sm: 32,
    md: 48,
    lg: 64,
    xl: 96,
    xxl: 128
  };

  const dimension = sizes[size] || sizes.md;

  return (
    <svg
      width={dimension}
      height={dimension}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`trophy-icon ${className}`}
      aria-label="Trophy icon"
    >
      <defs>
        <linearGradient id="trophy-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
          <stop offset="50%" stopColor="#e5e5e7" stopOpacity="0.9" />
          <stop offset="100%" stopColor="#d1d1d6" stopOpacity="0.85" />
        </linearGradient>
      </defs>

      {/* Trophy Cup */}
      <path
        d="M18 14h28v18c0 7.732-6.268 14-14 14s-14-6.268-14-14V14z"
        fill="url(#trophy-gradient)"
        stroke="#ffffff"
        strokeWidth="2"
        opacity="0.9"
      />

      {/* Left Handle */}
      <path
        d="M14 16h4v6c0 2.21-1.79 4-4 4s-4-1.79-4-4 1.79-4 4-4z"
        fill="url(#trophy-gradient)"
        stroke="#ffffff"
        strokeWidth="2"
        opacity="0.9"
      />

      {/* Right Handle */}
      <path
        d="M46 16h4c2.21 0 4 1.79 4 4s-1.79 4-4 4-4-1.79-4-4v-6z"
        fill="url(#trophy-gradient)"
        stroke="#ffffff"
        strokeWidth="2"
        opacity="0.9"
      />

      {/* Stem */}
      <rect
        x="28"
        y="46"
        width="8"
        height="6"
        fill="url(#trophy-gradient)"
        stroke="#ffffff"
        strokeWidth="2"
        opacity="0.9"
      />

      {/* Base */}
      <rect
        x="22"
        y="52"
        width="20"
        height="8"
        rx="2"
        fill="url(#trophy-gradient)"
        stroke="#ffffff"
        strokeWidth="2"
        opacity="0.9"
      />

      {/* Shine Effect */}
      <path
        d="M26 18c1.5 0 3 1.5 3 3s-1.5 3-3 3"
        stroke="#ffffff"
        strokeWidth="2"
        opacity="0.4"
        strokeLinecap="round"
      />
    </svg>
  );
}
