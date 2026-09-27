// Small inline SVG cat-themed icons. Inherit color via currentColor.

export function PawIcon({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" {...props}>
      <ellipse cx="6" cy="10" rx="2" ry="2.6" />
      <ellipse cx="10.5" cy="7" rx="2" ry="2.8" />
      <ellipse cx="15" cy="7" rx="2" ry="2.8" />
      <ellipse cx="18.5" cy="10.5" rx="2" ry="2.6" />
      <path d="M12 12c-2.6 0-5 1.9-5 4.4 0 1.8 1.5 2.6 3 2.6 1 0 1.4-.3 2-.3s1 .3 2 .3c1.5 0 3-.8 3-2.6 0-2.5-2.4-4.4-5-4.4z" />
    </svg>
  );
}

export function CatFaceIcon({ size = 24, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" {...props}>
      <path d="M4 4l3 4M20 4l-3 4" strokeLinecap="round" />
      <path d="M5 10c0-1 1-2 2-2h10c1 0 2 1 2 2v3a7 7 0 0 1-14 0v-3z" />
      <circle cx="9.5" cy="12" r="0.6" fill="currentColor" stroke="none" />
      <circle cx="14.5" cy="12" r="0.6" fill="currentColor" stroke="none" />
      <path d="M12 14v1M10.5 16c.5.4 2.5.4 3 0" strokeLinecap="round" />
    </svg>
  );
}
