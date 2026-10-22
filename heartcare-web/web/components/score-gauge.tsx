"use client";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export function ScoreGauge({ score, color }: { score: number; color: string }) {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) { setShown(score); return; }
    let raf = 0; const t0 = performance.now();
    const tick = (t: number) => {
      const p = Math.min((t - t0) / 1300, 1);
      setShown(Math.round(score * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [score]);

  const angle = -90 + (shown / 100) * 180;
  // arc from (30,140) to (270,140), r=120; filled portion
  const frac = shown / 100;
  const dashTotal = 377;
  return (
    <div className="flex flex-col items-center" role="img" aria-label={`Gauge showing score ${score} out of 100`}>
      <svg width="300" height="172" viewBox="0 0 300 172" className="max-w-full">
        <path d="M30 140 A120 120 0 0 1 270 140" fill="none"
          strokeWidth="18" strokeLinecap="round" className="stroke-muted" />
        <motion.path
          d="M30 140 A120 120 0 0 1 270 140" fill="none"
          stroke={color} strokeWidth="18" strokeLinecap="round" opacity={0.9}
          strokeDasharray={dashTotal}
          initial={{ strokeDashoffset: dashTotal }}
          animate={{ strokeDashoffset: dashTotal * (1 - frac) }}
          transition={{ duration: 1.3, ease: [0.22, 1, 0.36, 1] }}
        />
        <motion.g
          initial={{ rotate: -90 }}
          animate={{ rotate: angle }}
          transition={{ duration: 1.3, ease: [0.22, 1, 0.36, 1] }}
          style={{ transformOrigin: "150px 140px" }}
        >
          <line x1="150" y1="140" x2="150" y2="54" strokeWidth="3"
            strokeLinecap="round" className="stroke-foreground" />
          <circle cx="150" cy="140" r="7" className="fill-foreground" />
        </motion.g>
      </svg>
      <p className="text-muted-foreground text-[13px] tabular-nums">0 = critical · 100 = excellent</p>
    </div>
  );
}
