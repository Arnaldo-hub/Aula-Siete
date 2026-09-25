export default function Logo({ size = 34 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-label="Aula Site">
      <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#4f46e5"/><stop offset="1" stop-color="#7c3aed"/>
      </linearGradient></defs>
      <rect width="64" height="64" rx="14" fill="url(#lg)"/>
      <text x="32" y="43" fontFamily="Arial, sans-serif" fontSize="28" fontWeight="800"
            fill="#fff" textAnchor="middle">A7</text>
    </svg>
  )
}
