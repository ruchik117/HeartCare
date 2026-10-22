import type { HeartPayload } from "./api";

/** Label <-> dataset-code maps. Must mirror train_model.py / app.py exactly. */
export const SEX = { Female: 0, Male: 1 } as const;
export const CP: Record<string, number> = {
  "Typical angina": 1, "Atypical angina": 2, "Non-anginal pain": 3, "Asymptomatic": 4,
};
export const BOOL = { No: 0, Yes: 1 } as const;
export const RESTECG: Record<string, number> = {
  Normal: 0, "ST-T wave abnormality": 1, "Left ventricular hypertrophy": 2,
};
export const SLOPE: Record<string, number> = { Upsloping: 1, Flat: 2, Downsloping: 3 };
export const THAL: Record<string, number> = { Normal: 3, "Fixed defect": 6, "Reversible defect": 7 };

export const GRADE_HEX: Record<string, string> = {
  "A+": "#16a34a", A: "#22c55e", B: "#eab308",
  C: "#f97316", D: "#ef4444", F: "#991b1b",
};

/** Neutral defaults used by Quick mode (same as Streamlit app). */
export const QUICK_DEFAULTS = { fbs: 0, restecg: 0, ca: 0, oldpeak: 0.8, slope: 2, thal: 3 };

const num = (v: unknown, fb: number) => {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v))) return Number(v);
  return fb;
};
const pick = (v: unknown, table: Record<string, number>, fb: number) =>
  typeof v === "string" && v in table ? table[v] : fb;

/** Convert /api/demos human-label dicts into a POST-ready payload. */
export function demoToPayload(d: Record<string, string | number>, mode: "Quick" | "Clinical"): HeartPayload {
  return {
    age: num(d.age, 45),
    sex: pick(d.sex_label, SEX as unknown as Record<string, number>, 1),
    cp: pick(d.cp_label, CP, 4),
    trestbps: num(d.trestbps, 120),
    chol: num(d.chol, 200),
    fbs: pick(d.fbs_label, BOOL as unknown as Record<string, number>, 0),
    restecg: pick(d.restecg_label, RESTECG, 0),
    thalach: num(d.thalach, 150),
    exang: pick(d.exang_label, BOOL as unknown as Record<string, number>, 0),
    oldpeak: num(d.oldpeak, 0.8),
    slope: pick(d.slope_label, SLOPE, 2),
    ca: num(d.ca_label, 0),
    thal: pick(d.thal_label, THAL, 3),
    smoking: (d.smoking as HeartPayload["smoking"]) ?? "Never",
    activity: (["Low", "Moderate", "High"].includes(d.activity as string)
      ? d.activity
      : "Moderate") as HeartPayload["activity"],
    family_history: d.family_history === "Yes",
    bp_history: d.known_bp_history === "Yes",
    mode,
  };
}
