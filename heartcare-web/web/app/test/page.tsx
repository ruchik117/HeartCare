"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { FlaskConical, HeartPulse, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, type HeartPayload } from "@/lib/api";
import { BOOL, CP, QUICK_DEFAULTS, RESTECG, SEX, SLOPE, THAL, demoToPayload } from "@/lib/mapping";
import { useAssessment } from "@/lib/store";

const schema = z.object({
  mode: z.enum(["Quick", "Clinical"]),
  age: z.coerce.number().min(1).max(120),
  sex: z.coerce.number().int().min(0).max(1),
  cp: z.coerce.number().int().min(1).max(4),
  trestbps: z.coerce.number().min(50).max(250),
  chol: z.coerce.number().min(50).max(600),
  thalach: z.coerce.number().min(50).max(250),
  exang: z.coerce.number().int().min(0).max(1),
  fbs: z.coerce.number().int().min(0).max(1),
  restecg: z.coerce.number().int().min(0).max(2),
  ca: z.coerce.number().int().min(0).max(3),
  oldpeak: z.coerce.number().min(0).max(10),
  slope: z.coerce.number().int().min(1).max(3),
  thal: z.coerce.number().int().min(3).max(7),
  smoking: z.enum(["Never", "Former", "Current"]),
  activity: z.enum(["Low", "Moderate", "High"]),
  family_history: z.boolean(),
  bp_history: z.boolean(),
  patient_name: z.string().max(100).optional(),
});
type V = z.infer<typeof schema>;

const DEFAULTS: V = {
  mode: "Quick", age: 45, sex: 1, cp: 4, trestbps: 120, chol: 200,
  thalach: 150, exang: 0, fbs: 0, restecg: 0, ca: 0, oldpeak: 0.8,
  slope: 2, thal: 3, smoking: "Never", activity: "Moderate",
  family_history: false, bp_history: false, patient_name: "",
};

function Num({ label, hint, children, error }: {
  label: string; hint?: string; children: React.ReactNode; error?: string;
}) {
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between">
        <label className="text-sm font-semibold">{label}</label>
      </div>
      {children}
      {hint && <p className="text-muted-foreground mt-1 text-xs">{hint}</p>}
      {error && <p role="alert" className="mt-1 text-xs font-medium text-[#dc2626]">{error}</p>}
    </div>
  );
}

function Select({ label, value, onChange, options }: {
  label: string; value: string | number; onChange: (v: string) => void;
  options: { v: string | number; label: string }[];
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-semibold">{label}</span>
      <select
        value={value} onChange={(e) => onChange(e.target.value)}
        className="border-input bg-background w-full rounded-lg border px-3 py-2.5 text-sm"
      >
        {options.map((o) => <option key={o.v} value={o.v}>{o.label}</option>)}
      </select>
    </label>
  );
}

const opts = (t: Record<string, number>) => Object.entries(t).map(([label, v]) => ({ v, label }));

export default function TestPage() {
  const router = useRouter();
  const { setAssessment } = useAssessment();
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { control, register, handleSubmit, watch, setValue, reset, formState: { errors } } =
    useForm<V>({ resolver: zodResolver(schema), defaultValues: DEFAULTS });
  const mode = watch("mode");

  async function fillDemo(which: "healthy" | "at_risk") {
    setBusy(which); setError(null);
    try {
      const d = await api.demos();
      const src = which === "healthy" ? d.healthy : d.at_risk;
      reset({
        ...DEFAULTS, mode, patient_name: "",
        age: src.age as number, sex: SEX[src.sex_label as keyof typeof SEX] ?? 1,
        cp: CP[src.cp_label as string] ?? 4,
        trestbps: src.trestbps as number, chol: src.chol as number,
        thalach: src.thalach as number,
        exang: Number((BOOL as Record<string, number>)[src.exang_label as string] ?? 0),
        fbs: Number((BOOL as Record<string, number>)[(src.fbs_label as string) ?? "No"] ?? 0),
        restecg: RESTECG[src.restecg_label as string] ?? 0,
        ca: Number(src.ca_label ?? 0), oldpeak: (src.oldpeak as number) ?? 0.8,
        slope: SLOPE[src.slope_label as string] ?? 2,
        thal: THAL[src.thal_label as string] ?? 3,
        smoking: (src.smoking as V["smoking"]) ?? "Never",
        activity: (src.activity as V["activity"]) ?? "Moderate",
        family_history: src.family_history === "Yes",
        bp_history: src.known_bp_history === "Yes",
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backend unreachable");
    } finally { setBusy(null); }
  }

  async function onSubmit(v: V) {
    setError(null);
    const payload: HeartPayload = {
      age: v.age, sex: v.sex as 0 | 1, cp: v.cp as 1 | 2 | 3 | 4,
      trestbps: v.trestbps, chol: v.chol,
      fbs: (v.mode === "Quick" ? QUICK_DEFAULTS.fbs : v.fbs) as 0 | 1,
      restecg: (v.mode === "Quick" ? QUICK_DEFAULTS.restecg : v.restecg) as 0 | 1 | 2,
      thalach: v.thalach, exang: v.exang as 0 | 1,
      oldpeak: v.mode === "Quick" ? QUICK_DEFAULTS.oldpeak : v.oldpeak,
      slope: (v.mode === "Quick" ? QUICK_DEFAULTS.slope : v.slope) as 1 | 2 | 3,
      ca: (v.mode === "Quick" ? QUICK_DEFAULTS.ca : v.ca) as 0 | 1 | 2 | 3,
      thal: (v.mode === "Quick" ? QUICK_DEFAULTS.thal : v.thal) as 3 | 6 | 7,
      smoking: v.smoking, activity: v.activity,
      family_history: v.family_history, bp_history: v.bp_history, mode: v.mode,
      patient_name: v.patient_name?.trim() ? v.patient_name.trim() : undefined,
    };
    try {
      const response = await api.score(payload);
      setAssessment({ payload, response });
      router.push("/results");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scoring failed");
    }
  }

  return (
    <div className="pt-8">
      <h1 className="text-3xl font-extrabold tracking-tight">Heart health check</h1>
      <p className="text-muted-foreground mt-1.5">Quick needs 7 numbers. Clinical uses all 13 model features — from reports only, never guesses.</p>

      <Tabs value={mode} onValueChange={(m) => setValue("mode", m as V["mode"])} className="mt-5">
        <TabsList aria-label="Mode">
          <TabsTrigger value="Quick">Quick · 7 fields</TabsTrigger>
          <TabsTrigger value="Clinical">Clinical · 13 fields</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="mt-4 flex flex-wrap gap-2">
        <Button variant="outline" size="sm" disabled={busy !== null} onClick={() => fillDemo("healthy")}>
          {busy === "healthy" ? <Loader2 className="animate-spin" /> : <HeartPulse />} Fill healthy demo
        </Button>
        <Button variant="outline" size="sm" disabled={busy !== null} onClick={() => fillDemo("at_risk")}>
          {busy === "at_risk" ? <Loader2 className="animate-spin" /> : <FlaskConical />} Fill at-risk demo
        </Button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-5 grid gap-4">
        <Card className="shadow-sm">
          <CardHeader><CardTitle className="text-lg">About you</CardTitle>
            <CardDescription>Name only labels your PDF report — it is never scored.</CardDescription></CardHeader>
          <CardContent className="grid gap-6 p-6 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1.5 block text-sm font-semibold">Name (optional)</span>
              <input {...register("patient_name")} placeholder="e.g. Alex" maxLength={100}
                className="border-input bg-background w-full rounded-lg border px-3 py-2.5 text-sm" />
            </label>
            <Controller name="age" control={control} render={({ field }) => (
              <Num label="Age (years)" hint="18–100 on this form." error={errors.age?.message}>
                <input type="number" min={18} max={100} step={1} value={field.value ?? ""}
                  onChange={(e) => field.onChange(e.target.value === "" ? undefined : Number(e.target.value))}
                  placeholder="e.g. 45" aria-label="Age in years"
                  className="border-input bg-background w-full rounded-lg border px-3 py-2.5 text-sm tabular-nums" />
              </Num>
            )} />
            <Controller name="sex" control={control} render={({ field }) => (
              <Select label="Sex (dataset coding)" value={field.value} onChange={field.onChange}
                options={opts(SEX)} />
            )} />
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader><CardTitle className="text-lg">Vitals you likely know</CardTitle>
            <CardDescription>Use measured values from a device or recent check-up.</CardDescription></CardHeader>
          <CardContent className="grid gap-6 p-6 sm:grid-cols-2">
            <Controller name="cp" control={control} render={({ field }) => (
              <Select label="Chest pain category" value={field.value} onChange={field.onChange} options={opts(CP)} />
            )} />
            <Controller name="trestbps" control={control} render={({ field }) => (
              <Num label={`Resting BP — ${field.value} mm Hg`} error={errors.trestbps?.message}>
                <Slider min={50} max={250} step={1} value={[field.value]} onValueChange={(v) => field.onChange(Array.isArray(v) ? v[0] : v)} aria-label="Resting blood pressure" />
              </Num>
            )} />
            <Controller name="chol" control={control} render={({ field }) => (
              <Num label={`Cholesterol — ${field.value} mg/dL`} error={errors.chol?.message}>
                <Slider min={50} max={600} step={1} value={[field.value]} onValueChange={(v) => field.onChange(Array.isArray(v) ? v[0] : v)} aria-label="Cholesterol" />
              </Num>
            )} />
            <Controller name="thalach" control={control} render={({ field }) => (
              <Num label={`Max heart rate — ${field.value} bpm`} error={errors.thalach?.message}>
                <Slider min={50} max={250} step={1} value={[field.value]} onValueChange={(v) => field.onChange(Array.isArray(v) ? v[0] : v)} aria-label="Maximum heart rate" />
              </Num>
            )} />
            <Controller name="exang" control={control} render={({ field }) => (
              <Select label="Exercise-induced angina?" value={field.value} onChange={field.onChange} options={opts(BOOL)} />
            )} />
          </CardContent>
        </Card>

        {mode === "Clinical" ? (
          <Card className="shadow-sm">
            <CardHeader><CardTitle className="text-lg">Clinical — reports only</CardTitle>
              <CardDescription>Copy values from an ECG or lab report. Do not estimate.</CardDescription></CardHeader>
            <CardContent className="grid gap-6 p-6 sm:grid-cols-2">
              <Controller name="fbs" control={control} render={({ field }) => (
                <Select label="Fasting sugar above 120?" value={field.value} onChange={field.onChange} options={opts(BOOL)} />
              )} />
              <Controller name="restecg" control={control} render={({ field }) => (
                <Select label="Resting ECG" value={field.value} onChange={field.onChange} options={opts(RESTECG)} />
              )} />
              <Controller name="ca" control={control} render={({ field }) => (
                <Select label="Vessels seen (fluoroscopy)" value={field.value} onChange={field.onChange}
                  options={[{ v: 0, label: "0" }, { v: 1, label: "1" }, { v: 2, label: "2" }, { v: 3, label: "3" }]} />
              )} />
              <Controller name="oldpeak" control={control} render={({ field }) => (
                <Num label={`ST depression — ${Number(field.value).toFixed(1)}`} error={errors.oldpeak?.message}>
                  <Slider min={0} max={10} step={0.1} value={[field.value]} onValueChange={(v) => field.onChange(Array.isArray(v) ? v[0] : v)} aria-label="ST depression" />
                </Num>
              )} />
              <Controller name="slope" control={control} render={({ field }) => (
                <Select label="ST slope" value={field.value} onChange={field.onChange} options={opts(SLOPE)} />
              )} />
              <Controller name="thal" control={control} render={({ field }) => (
                <Select label="Thal test result" value={field.value} onChange={field.onChange} options={opts(THAL)} />
              )} />
            </CardContent>
          </Card>
        ) : (
          <p className="text-muted-foreground text-sm">Quick mode fills ECG, ST, vessels and thal with neutral defaults and tells you on the result screen.</p>
        )}

        <Card className="shadow-sm">
          <CardHeader><CardTitle className="text-lg">Lifestyle</CardTitle>
            <CardDescription>Shown on your report. Not model inputs — the dataset never recorded them.</CardDescription></CardHeader>
          <CardContent className="grid gap-6 p-6 sm:grid-cols-2">
            <label className="block"><span className="mb-1.5 block text-sm font-semibold">Smoking</span>
              <select {...register("smoking")} className="border-input bg-background w-full rounded-lg border px-3 py-2.5 text-sm">
                <option>Never</option><option>Former</option><option>Current</option>
              </select></label>
            <label className="block"><span className="mb-1.5 block text-sm font-semibold">Physical activity</span>
              <select {...register("activity")} className="border-input bg-background w-full rounded-lg border px-3 py-2.5 text-sm">
                <option>Low</option><option>Moderate</option><option>High</option>
              </select></label>
            <label className="flex items-center gap-2.5 text-sm font-medium">
              <input type="checkbox" {...register("family_history")} className="size-4 accent-[#3b82f6]" /> Family history of heart disease</label>
            <label className="flex items-center gap-2.5 text-sm font-medium">
              <input type="checkbox" {...register("bp_history")} className="size-4 accent-[#3b82f6]" /> History of high blood pressure</label>
          </CardContent>
        </Card>

        {error && <p role="alert" className="text-sm font-medium text-[#dc2626]">{error}</p>}
        <Button type="submit" size="lg" className="w-full sm:w-auto">See my score</Button>
      </form>
    </div>
  );
}
