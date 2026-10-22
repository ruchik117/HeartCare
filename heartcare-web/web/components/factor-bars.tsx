"use client";
import { motion } from "framer-motion";
import type { ScoreResponse } from "@/lib/api";
import { GRADE_HEX } from "@/lib/mapping";
import { cn } from "@/lib/utils";

export function FactorBars({ factors }: { factors: ScoreResponse["factors"] }) {
  const max = Math.max(...factors.map((f) => Math.abs(f.impact)), 0.001);
  return (
    <div>
      {factors.map((f, i) => {
        const pct = Math.max(8, (Math.abs(f.impact) / max) * 100);
        const bar = f.direction === "raising" ? GRADE_HEX.D : f.direction === "lowering" ? GRADE_HEX["A+"] : "#94a3b8";
        return (
          <div key={f.feature} className={cn("py-3.5", i > 0 && "border-t")}>
            <div className="mb-2 flex items-baseline justify-between">
              <b className="text-[14.5px]">{f.friendly}</b>
              <span
                className="rounded-full px-2.5 py-0.5 text-[11.5px] font-bold"
                style={{
                  color: bar, backgroundColor: `${bar}1f`,
                }}
              >
                {f.direction === "raising" ? "▲ raising" : f.direction === "lowering" ? "▼ lowering" : "– neutral"}
              </span>
            </div>
            <div className="h-2.5 overflow-hidden rounded-full bg-muted">
              <motion.div
                className="h-full rounded-full"
                style={{ backgroundColor: bar }}
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 1, delay: 0.15 + i * 0.12, ease: [0.22, 1, 0.36, 1] }}
              />
            </div>
            <p className="text-muted-foreground mt-1.5 text-[12.5px]">
              {f.hint ? `${f.hint} · impact ` : "Impact "}{f.impact > 0 ? "+" : ""}{f.impact}
            </p>
          </div>
        );
      })}
    </div>
  );
}
