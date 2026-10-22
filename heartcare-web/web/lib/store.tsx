"use client";
import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import type { HeartPayload, ScoreResponse } from "./api";

export interface Assessment {
  payload: HeartPayload;
  response: ScoreResponse;
}

const Ctx = createContext<{
  assessment: Assessment | null;
  setAssessment: (a: Assessment) => void;
  clear: () => void;
} | null>(null);

export function ScoreProvider({ children }: { children: ReactNode }) {
  const [assessment, set] = useState<Assessment | null>(null);
  const setAssessment = useCallback((a: Assessment) => set(a), []);
  const clear = useCallback(() => set(null), []);
  return <Ctx.Provider value={{ assessment, setAssessment, clear }}>{children}</Ctx.Provider>;
}

export function useAssessment() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAssessment outside ScoreProvider");
  return v;
}
