export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ScoreResponse {
  score: number;
  grade: string;
  label: string;
  color: string;
  bg: string;
  advice: string;
  model_proba: number;
  prediction: number;
  breakdown: { model: number; lifestyle: number; vitals: number };
  reasons: string[];
  factors: { feature: string; friendly: string; impact: number; direction: string; hint: string }[];
  disclaimer: string;
}

export interface HeartPayload {
  age: number; sex: number; cp: number; trestbps: number; chol: number;
  fbs: number; restecg: number; thalach: number; exang: number; oldpeak: number;
  slope: number; ca: number; thal: number;
  smoking: "Never" | "Former" | "Current";
  activity: "Low" | "Moderate" | "High";
  family_history: boolean; bp_history: boolean; mode: "Quick" | "Clinical";
  patient_name?: string;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status} on ${path}: ${text.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => req<{ status: string; model: string }>("/api/health"),
  score: (p: HeartPayload) =>
    req<ScoreResponse>("/api/score", { method: "POST", body: JSON.stringify(p) }),
  report: async (p: HeartPayload): Promise<Blob> => {
    const res = await fetch(`${API_BASE}/api/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(p),
    });
    if (!res.ok) throw new Error(`Report failed: ${res.status}`);
    return res.blob();
  },
  modelInfo: () =>
    req<{
      model_name: string;
      metrics: Record<string, string | number>;
      features: string[];
      dataset: string;
      comparison: Record<string, string | number>[];
      disclaimer: string;
    }>("/api/model-info"),
  demos: () =>
    req<{ healthy: Record<string, string | number>; at_risk: Record<string, string | number> }>(
      "/api/demos"
    ),
};
