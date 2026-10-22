"use client";
import { motion } from "framer-motion";
import { ArrowRight, BrainCircuit, FileText, FlaskConical, HeartPulse, Stethoscope } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { demoToPayload } from "@/lib/mapping";
import { useAssessment } from "@/lib/store";

const rise = { initial: { opacity: 0, y: 18 }, animate: { opacity: 1, y: 0 } };

const GRADES: [string, string, string][] = [
  ["A+", "#16a34a", "90–100"],
  ["A", "#22c55e", "80–89"],
  ["B", "#eab308", "70–79"],
  ["C", "#f97316", "60–69"],
  ["D", "#ef4444", "50–59"],
  ["F", "#991b1b", "below 50"],
];

export default function Home() {
  const router = useRouter();
  const { setAssessment } = useAssessment();
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [f1, setF1] = useState<string | null>(null);

  useEffect(() => {
    api.modelInfo().then((m) => setF1(String(m.metrics?.["F1 Score"] ?? ""))).catch(() => {});
  }, []);

  async function tryDemo(which: "healthy" | "at_risk") {
    setBusy(which); setError(null);
    try {
      const d = await api.demos();
      const payload = demoToPayload(which === "healthy" ? d.healthy : d.at_risk, "Clinical");
      const response = await api.score(payload);
      setAssessment({ payload, response });
      router.push("/results");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backend unreachable. Start it with bash run.sh");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <motion.section {...rise} transition={{ duration: 0.5 }} className="pb-10 pt-14">
        <h1 className="max-w-3xl text-[clamp(38px,6vw,68px)] font-extrabold leading-[1.02] tracking-[-0.035em]">
          Know your heart, <span className="text-[#16a34a]">without the jargon.</span>
        </h1>
        <p className="text-muted-foreground mt-5 max-w-[62ch] text-[17px] leading-relaxed">
          Answer a guided check, get a clear <b>score from 0–100 with a grade from A+ to F</b>,
          see what lifted or lowered it, and leave with habits worth discussing with a clinician.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <Button size="lg" onClick={() => router.push("/test")}>
            Take the health test <ArrowRight />
          </Button>
          <Button size="lg" variant="outline" disabled={busy !== null} onClick={() => tryDemo("healthy")}>
            <HeartPulse /> {busy === "healthy" ? "Scoring…" : "Try healthy demo"}
          </Button>
          <Button size="lg" variant="outline" disabled={busy !== null} onClick={() => tryDemo("at_risk")}>
            <FlaskConical /> {busy === "at_risk" ? "Scoring…" : "Try at-risk demo"}
          </Button>
        </div>
        {error && <p role="alert" className="mt-3 text-sm font-medium text-[#dc2626]">{error}</p>}
        <dl className="mt-9 grid max-w-2xl grid-cols-2 gap-3 sm:grid-cols-4">
          {[["F1 score", f1 ?? "…"], ["Records", "303"], ["Models compared", "3"], ["Inputs", "13"]].map(([k, v]) => (
            <div key={k} className="border bg-card rounded-2xl border p-4 shadow-sm">
              <dd className="text-2xl font-extrabold tabular-nums tracking-tight">{v}</dd>
              <dt className="text-muted-foreground mt-0.5 text-xs">{k}</dt>
            </div>
          ))}
        </dl>
      </motion.section>

      <motion.section {...rise} transition={{ duration: 0.5, delay: 0.06 }}>
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>One glance, six grades</CardTitle>
            <CardDescription>Your result lands on this scale — color, letter, and plain words.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-2.5 sm:grid-cols-6">
              {GRADES.map(([g, c, band]) => (
                <div key={g} className="rounded-xl border p-3 text-center" style={{ borderColor: `${c}55`, background: `${c}14` }}>
                  <div className="text-2xl font-extrabold" style={{ color: c }}>{g}</div>
                  <div className="text-muted-foreground mt-0.5 text-xs tabular-nums">{band}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.section>

      <motion.section {...rise} transition={{ duration: 0.5, delay: 0.1 }} className="mt-4 grid gap-4 md:grid-cols-3">
        {[
          { n: "Step 1", icon: Stethoscope, t: "Answer", d: "Seven numbers in Quick mode, thirteen with lab reports in Clinical. Plain labels, no codes." },
          { icon: BrainCircuit, n: "Step 2", t: "Get your score", d: "A grade badge, an animated gauge, and the top model factors behind your result." },
          { icon: FileText, n: "Step 3", t: "Take it with you", d: "Download a one-page PDF with your score, reasons, and numbers for your records." },
        ].map((c) => (
          <Card key={c.t} className="shadow-sm">
            <CardHeader>
              <span className="text-muted-foreground text-xs font-bold tracking-wide">{c.n}</span>
              <CardTitle className="mt-1 flex items-center gap-2 text-lg"><c.icon className="size-5" />{c.t}</CardTitle>
              <CardDescription className="text-[14px] leading-relaxed">{c.d}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </motion.section>

      <motion.section {...rise} transition={{ duration: 0.5, delay: 0.14 }} className="mt-4">
        <Card className="border-[#3b82f6]/30 bg-gradient-to-br from-[#3b82f6]/8 to-transparent shadow-sm">
          <CardContent className="flex flex-col items-start justify-between gap-4 p-6 sm:flex-row sm:items-center sm:p-7">
            <div>
              <CardTitle className="text-xl">Logistic Regression · F1 {f1 ?? "…"}</CardTitle>
              <CardDescription className="mt-1 max-w-[52ch] text-[14px]">
                Three classifiers trained and compared on the UCI Cleveland set. See the full
                comparison, the scoring formula, and the limits of a 303-row classroom dataset.
              </CardDescription>
            </div>
            <Button variant="outline" onClick={() => router.push("/about")}>How the model works <ArrowRight /></Button>
          </CardContent>
        </Card>
      </motion.section>

      <motion.section {...rise} transition={{ duration: 0.5, delay: 0.18 }} className="mt-4">
        <Card className="bg-[#0B1E3A] text-white shadow-md dark:bg-[#13294B]">
          <CardContent className="flex flex-col items-start justify-between gap-4 p-6 sm:flex-row sm:items-center sm:p-8">
            <div>
              <CardTitle className="text-2xl tracking-tight text-white">Ready when you are.</CardTitle>
              <CardDescription className="mt-1 text-[15px] text-[#B9C6DA]">Two minutes, seven numbers, one clear grade.</CardDescription>
            </div>
            <Button size="lg" onClick={() => router.push("/test")} className="bg-[#0E9384] text-white hover:bg-[#0B7A6E]">
              Start the check <ArrowRight />
            </Button>
          </CardContent>
        </Card>
      </motion.section>
    </div>
  );
}
