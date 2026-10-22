"use client";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function AboutPage() {
  const [info, setInfo] = useState<Awaited<ReturnType<typeof api.modelInfo>> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.modelInfo()
      .then((d) => setInfo({
        ...d,
        comparison: d.comparison.map((r) => ({
          ...r,
          ...Object.fromEntries(
            ["Accuracy", "Precision", "Recall", "F1 Score"]
              .filter((k) => k in r)
              .map((k) => [k, Number(r[k])])
          ),
        })),
      }))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, []);

  return (
    <div className="pt-8">
      <h1 className="text-3xl font-extrabold tracking-tight">The model behind the score</h1>
      <p className="text-muted-foreground mt-1.5 max-w-[68ch]">
        A classroom comparison of three classifiers on the UCI Cleveland heart-disease subset
        (303 records, 1980s, single site). Selected by F1 score — a teaching choice, not clinical validation.
      </p>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>F1 comparison (higher is better)</CardTitle>
          <CardDescription>20% stratified holdout · random_state 42 · live from the training run</CardDescription>
        </CardHeader>
        <CardContent>
          {error && <p role="alert" className="text-sm font-medium text-[#dc2626]">{error} — start the backend with bash run.sh</p>}
          {info ? (
            <>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={info.comparison} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis dataKey="Model" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0.5, 1]} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="F1 Score" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-muted-foreground border-b text-left">
                      {Object.keys(info.comparison[0] ?? {}).map((k) => <th key={k} className="py-2 pr-4 font-semibold">{k}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {info.comparison.map((row) => (
                      <tr key={row.Model} className="border-b last:border-0">
                        {Object.values(row).map((v, i) => <td key={i} className="py-2 pr-4 tabular-nums">{v}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="text-muted-foreground mt-3 text-sm">Selected model: <b className="text-foreground">{info.model_name}</b> · {info.dataset}</p>
            </>
          ) : !error && <p className="text-muted-foreground text-sm">Loading model data…</p>}
        </CardContent>
      </Card>

      <Card className="mt-4">
        <CardHeader><CardTitle>How the 0–100 score is built</CardTitle></CardHeader>
        <CardContent className="text-muted-foreground space-y-2 text-sm leading-relaxed">
          <p><b className="text-foreground">Score = 100 − (40 × model probability + lifestyle penalty + vitals penalty).</b></p>
          <p>Lifestyle: current smoking +1.0, former +0.5, low activity +0.6, moderate +0.3, family history +0.4, BP history +0.5 (capped, ×15).</p>
          <p>Vitals: BP &gt;140 +0.5, cholesterol &gt;240 +0.5, ST depression &gt;2 +0.5, low max heart rate +0.25 (capped, ×15).</p>
          <p>Explainability: each input value × the logistic-regression coefficient, grouped back to the 13 fields — top 3 shown.</p>
        </CardContent>
      </Card>

      <p className="mt-4 rounded-xl border p-4 text-center text-[13px] font-medium text-muted-foreground">
        {info?.disclaimer ?? "Educational only — not a medical device."}
      </p>
    </div>
  );
}
