import { Activity, Apple, BedDouble, CigaretteOff, HeartHandshake, Stethoscope } from "lucide-react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const TIPS = [
  { icon: Apple, t: "Eat balanced", d: "Vegetables, fruit, whole grains and suitable protein. Less salt and ultra-processed food." },
  { icon: Activity, t: "Move often", d: "Regular activity that fits your health. Consistency beats intensity." },
  { icon: CigaretteOff, t: "Avoid tobacco", d: "No smoking or chewing tobacco. Ask for help quitting — it is the single biggest lever." },
  { icon: Stethoscope, t: "Get checked", d: "Track blood pressure and cholesterol as your clinician recommends." },
  { icon: BedDouble, t: "Sleep steady", d: "Keep a regular schedule. Flag snoring or gasping to a doctor." },
  { icon: HeartHandshake, t: "Ease stress", d: "Walk, breathe, connect. Small routines compound." },
];

const GLOSSARY: [string, string][] = [
  ["Resting BP", "Pressure in your arteries at rest. Under 120 is typical; above 140 is high."],
  ["Cholesterol", "Fat-like substance in blood. Under 200 mg/dL is desirable; above 240 is high."],
  ["Max heart rate", "Highest rate reached during exercise. Rough estimate: 220 minus age."],
  ["ST depression", "Dip on an ECG after exercise. Higher values can signal strain — a clinician reads this."],
  ["Thal", "A nuclear imaging result: normal, fixed defect, or reversible defect. Report-only field."],
  ["Vessels (ca)", "How many major vessels showed in fluoroscopy (0–3). Report-only field."],
];

export default function TipsPage() {
  return (
    <div className="pt-8">
      <h1 className="text-3xl font-extrabold tracking-tight">Everyday habits</h1>
      <p className="text-muted-foreground mt-1.5">General wellness — not medical advice for any individual.</p>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {TIPS.map((x) => (
          <Card key={x.t}>
            <CardHeader>
              <span className="bg-muted text-foreground mb-1 flex size-10 items-center justify-center rounded-xl">
                <x.icon className="size-5" />
              </span>
              <CardTitle>{x.t}</CardTitle>
              <CardDescription>{x.d}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
      <h2 className="mt-8 text-xl font-extrabold tracking-tight">What each input means</h2>
      <dl className="mt-3 grid gap-3 sm:grid-cols-2">
        {GLOSSARY.map(([t, d]) => (
          <div key={t} className="border bg-card rounded-xl border p-4">
            <dt className="text-sm font-bold">{t}</dt>
            <dd className="text-muted-foreground mt-1 text-sm">{d}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-4 rounded-xl border border-[#dc2626]/40 bg-[#fef2f2] p-4 text-center text-sm font-semibold text-[#991b1b] dark:bg-[#450a0a] dark:text-[#fecaca]">
        Chest pain, severe breathlessness, fainting? Get urgent care now — not this website.
      </p>
    </div>
  );
}
