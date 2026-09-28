export default function Logo({ size = 34 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-label="Aula Siete">
      <defs>
        <linearGradient id="lgA7" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#312e81" />
          <stop offset=".55" stopColor="#4f46e5" />
          <stop offset="1" stopColor="#7c3aed" />
        </linearGradient>
      </defs>
      <rect width="64" height="64" rx="15" fill="url(#lgA7)" />
      <path d="M10 50 Q32 40 54 50 L54 56 Q32 47 10 56 Z" fill="#f97316" opacity=".9" />
      <text x="22" y="42" fontFamily="Arial Black, Arial, sans-serif" fontSize="30" fontWeight="900"
            fill="#ffffff" textAnchor="middle">A</text>
      <text x="43" y="42" fontFamily="Arial Black, Arial, sans-serif" fontSize="30" fontWeight="900"
            fill="#fdba74" textAnchor="middle">7</text>
    </svg>
  )
}
