"use client";
import { motion } from "framer-motion";
import { Download, RotateCcw, TriangleAlert } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FactorBars } from "@/components/factor-bars";
import { ScoreGauge } from "@/components/score-gauge";
import { api } from "@/lib/api";
import { demoToPayload } from "@/lib/mapping";
import { useAssessment } from "@/lib/store";

export default function ResultsPage() {
  return (
    <Suspense fallback={<p className="text-muted-foreground pt-12 text-center">Loading result…</p>}>
      <ResultsInner />
    </Suspense>
  );
}

function ResultsInner() {
  const router = useRouter();
  const search = useSearchParams();
  const { assessment, setAssessment } = useAssessment();
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Shareable demo link: /results?demo=at_risk (or =healthy)
  useEffect(() => {
    const which = search.get("demo");
    if (!assessment && (which === "at_risk" || which === "healthy")) {
      (async () => {
        setLoadingDemo(true);
        try {
          const d = await api.demos();
          const payload = demoToPayload(which === "healthy" ? d.healthy : d.at_risk, "Clinical");
          setAssessment({ payload, response: await api.score(payload) });
        } catch (e) {
          setError(e instanceof Error ? e.message : "Backend unreachable");
        } finally { setLoadingDemo(false); }
      })();
    }
  }, []);

  async function loadDemo() {
    setLoadingDemo(true); setError(null);
    try {
      const d = await api.demos();
      const payload = demoToPayload(d.at_risk, "Clinical");
      setAssessment({ payload, response: await api.score(payload) });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backend unreachable");
    } finally { setLoadingDemo(false); }
  }

  if (!assessment) {
    return (
      <div className="pt-12 text-center">
        <h1 className="text-3xl font-extrabold tracking-tight">No result yet</h1>
        <p className="text-muted-foreground mt-2">Take the health test first — it takes under two minutes.</p>
        <div className="mt-6 flex justify-center gap-2.5">
          <Button size="lg" onClick={() => router.push("/test")}>Take the health test</Button>
          <Button size="lg" variant="outline" disabled={loadingDemo} onClick={loadDemo}>
            {loadingDemo ? "Scoring…" : "Preview with demo data"}
          </Button>
        </div>
        {error && <p role="alert" className="mt-3 text-sm font-medium text-[#dc2626]">{error}</p>}
      </div>
    );
  }
  const { payload, response: r } = assessment;
  const total = r.breakdown.model + r.breakdown.lifestyle + r.breakdown.vitals;
  const segs = [
    { label: "Model pattern", v: r.breakdown.model, c: "#3b82f6" },
    { label: "Lifestyle", v: r.breakdown.lifestyle, c: "#eab308" },
    { label: "Vitals", v: r.breakdown.vitals, c: "#f97316" },
  ];

  async function downloadPdf() {
    setDownloading(true); setError(null);
    try {
      const blob = await api.report(payload);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "heartcare_report.pdf"; a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "PDF download failed");
    } finally { setDownloading(false); }
  }

  return (
    <div className="pt-8">
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
        <p className="text-muted-foreground text-[13px] font-semibold">Results · {payload.mode} mode</p>
        <h1 className="mt-1 text-3xl font-extrabold tracking-tight sm:text-4xl">Your heart score is ready.</h1>
        <p className="text-muted-foreground mt-2 max-w-[62ch]">
          One grade, three deductions, three reasons. A conversation starter with a clinician — never a diagnosis.
        </p>
      </motion.div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[340px_1fr]">
        <Card>
          <CardHeader><CardTitle className="text-muted-foreground text-[13px]">GRADE</CardTitle></CardHeader>
          <CardContent className="flex flex-col items-center text-center">
            <motion.div
              initial={{ scale: 0.85, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="flex size-40 items-center justify-center rounded-full border-[3px]"
              style={{ borderColor: r.color, background: `radial-gradient(circle at 50% 38%, ${r.color}22, transparent 70%)` }}
              role="img" aria-label={`Grade ${r.grade}, ${r.label}, score ${r.score} out of 100`}
            >
              <span className="text-7xl font-extrabold tracking-tight" style={{ color: r.color }}>{r.grade}</span>
            </motion.div>
            <p className="mt-3 text-4xl font-extrabold tracking-tight tabular-nums">
              {r.score}<span className="text-muted-foreground text-base font-semibold">/100</span>
            </p>
            <p className="mt-1 text-[15px] font-bold" style={{ color: r.color }}>{r.label}</p>
            <p className="text-muted-foreground mt-1.5 text-[13.5px]">{r.advice}</p>
            <p className="text-muted-foreground mt-3 text-xs tabular-nums">
              Model pattern {(r.model_proba * 100).toFixed(0)}% · {payload.mode} mode
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-muted-foreground text-[13px]">SCORE GAUGE</CardTitle></CardHeader>
          <CardContent className="flex flex-col items-center">
            <ScoreGauge score={r.score} color={r.color} />
            <div className="mt-4 flex flex-wrap justify-center gap-2.5">
              <Button onClick={downloadPdf} disabled={downloading}>
                <Download /> {downloading ? "Preparing…" : "Download PDF report"}
              </Button>
              <Button variant="outline" onClick={() => router.push("/test")}><RotateCcw /> Start over</Button>
            </div>
            {error && <p role="alert" className="mt-2 text-sm font-medium text-[#dc2626]">{error}</p>}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle className="text-muted-foreground text-[13px]">
            WHAT SHAPED YOUR SCORE (−{total.toFixed(1)} TOTAL)
          </CardTitle></CardHeader>
          <CardContent>
            <div className="bg-muted flex h-4 overflow-hidden rounded-full" aria-hidden>
              {segs.map((s) => (
                <motion.div key={s.label} style={{ backgroundColor: s.c }}
                  initial={{ width: 0 }} animate={{ width: `${total ? (s.v / total) * 100 : 0}%` }}
                  transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }} />
              ))}
            </div>
            <div className="mt-3 grid gap-3 sm:grid-cols-3">
              {segs.map((s) => (
                <div key={s.label} className="border bg-card rounded-xl border p-3">
                  <b className="text-xl tabular-nums" style={{ color: s.c }}>−{s.v.toFixed(1)}</b>
                  <p className="text-muted-foreground text-xs">{s.label}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle className="text-muted-foreground text-[13px]">WHY THE MODEL THINKS SO</CardTitle></CardHeader>
          <CardContent>
            <FactorBars factors={r.factors} />
            <div className="mt-4 space-y-2">
              {r.reasons.map((x) => (
                <p key={x} className="flex items-start gap-2 rounded-xl border border-[#fdba74] bg-[#fff7ed] px-3 py-2.5 text-sm text-[#7c2d12] dark:border-[#9a3412] dark:bg-[#431407] dark:text-[#fed7aa]">
                  <TriangleAlert className="mt-0.5 size-4 shrink-0" /> {x}
                </p>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {payload.mode === "Quick" && (
        <p className="text-muted-foreground mt-4 text-sm">
          Quick mode used neutral defaults for ECG, ST, vessels and thal. Retake in Clinical mode with lab reports for the full picture.
        </p>
      )}
      <p className="mt-4 rounded-xl border p-4 text-center text-[13px] font-medium text-muted-foreground">{r.disclaimer}</p>
    </div>
  );
}
