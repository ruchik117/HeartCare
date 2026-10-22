"use client";
import { ThemeProvider } from "next-themes";
import { useSearchParams } from "next/navigation";
import { Suspense, type ReactNode } from "react";

function Inner({ children }: { children: ReactNode }) {
  const q = useSearchParams();
  const forced = q.get("theme") === "dark" || q.get("theme") === "light" ? (q.get("theme") as "dark" | "light") : undefined;
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false} forcedTheme={forced}>
      {children}
    </ThemeProvider>
  );
}

export function ThemeSetup({ children }: { children: ReactNode }) {
  return (
    <Suspense>
      <Inner>{children}</Inner>
    </Suspense>
  );
}
