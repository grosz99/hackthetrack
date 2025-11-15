export default function LightningIcon({ size = 'md', className = '' }) {
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
      className={`lightning-icon ${className}`}
      aria-label="Lightning icon"
    >
      <path
        d="M36 4L20 32H32L28 60L44 32H32L36 4Z"
        fill="#f59e0b"
        stroke="#d97706"
        strokeWidth="2"
        strokeLinejoin="miter"
      />
    </svg>
  );
}
