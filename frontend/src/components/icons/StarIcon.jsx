export default function StarIcon({ size = 'md', className = '' }) {
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
      className={`star-icon ${className}`}
      aria-label="Star icon"
    >
      <path
        d="M32 8L38.472 26.944L58 29.528L44 42.472L48.944 62L32 51.056L15.056 62L20 42.472L6 29.528L25.528 26.944L32 8Z"
        fill="#FFD700"
        stroke="#FFA500"
        strokeWidth="2"
      />
    </svg>
  );
}
