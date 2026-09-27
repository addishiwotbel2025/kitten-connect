import { useEffect, useState } from "react";

// Auto-discover every image in src/assets/backgrounds/ at build time.
// You just drop files in that folder — no need to list them here.
const modules = import.meta.glob(
  "../assets/backgrounds/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP}",
  { eager: true }
);
const IMAGES = Object.values(modules).map((m) => m.default);

const ROTATE_MS = 6000; // fade to a new cat every 6 seconds

export default function BackgroundRotator() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (IMAGES.length <= 1) return; // nothing to rotate
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % IMAGES.length);
    }, ROTATE_MS);
    return () => clearInterval(id);
  }, []);

  // No images provided yet → warm ginger gradient fallback.
  if (IMAGES.length === 0) {
    return <div className="bg-layer bg-fallback" />;
  }

  return (
    <div className="bg-root">
      {IMAGES.map((src, i) => (
        <div
          key={src}
          className="bg-layer"
          style={{
            backgroundImage: `url(${src})`,
            opacity: i === index ? 1 : 0,
          }}
        />
      ))}
      {/* Ginger wash over the photos so text stays readable */}
      <div className="bg-tint" />
    </div>
  );
}
