"use client";
import { HeartPulse, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/test", label: "Health Test" },
  { href: "/results", label: "Results" },
  { href: "/about", label: "Model" },
  { href: "/tips", label: "Tips" },
];

export function SiteNav() {
  const { theme, setTheme } = useTheme();
  const path = usePathname();
  return (
    <header className="border-b">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-2 px-4 sm:px-6 sm:py-3.5">
        <Link href="/" className="flex shrink-0 items-center gap-2.5">
          <span className="flex size-8 items-center justify-center rounded-[10px] bg-gradient-to-br from-[#ef4444] to-[#f97316]">
            <HeartPulse className="size-4.5 text-white" strokeWidth={2.4} />
          </span>
          <span className="text-[17px] font-extrabold tracking-tight">HeartCare</span>
        </Link>
        <nav className="flex items-center gap-1 overflow-x-auto" aria-label="Primary">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={cn(
                "rounded-lg px-3 py-1.5 text-sm font-medium",
                path === l.href ? "bg-muted text-foreground" : "text-muted-foreground hover:text-foreground"
              )}
            >
              {l.label}
            </Link>
          ))}
          <Button
            variant="ghost" size="icon" className="ml-2 shrink-0"
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <Sun className="size-4.5 hidden dark:block" />
            <Moon className="size-4.5 dark:hidden" />
          </Button>
        </nav>
      </div>
    </header>
  );
}

export function DisclaimerBanner() {
  return (
    <div className="bg-[#7c2d12] px-4 py-2 text-center text-[13px] font-semibold text-[#ffedd5] dark:bg-[#431407]">
      EDUCATIONAL ONLY — <b>not a medical device.</b> Small 1980s dataset, not clinically validated.
    </div>
  );
}
