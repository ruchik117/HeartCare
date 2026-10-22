"""HeartCare FastAPI backend — thin wrapper over the frozen ML core.

ML logic lives in ../utils/ (score, explain, report) and is imported as-is.
This file adds HTTP transport + validation only. No formula changes.
"""

import csv
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# ML core lives one level up (COD/HeartCare/{utils,models})
ROOT = Path(__file__).resolve().parents[1].parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.schemas import HeartInput, ScoreResponse  # noqa: E402
from utils.demo import AT_RISK_DEMO, HEALTHY_DEMO  # noqa: E402
from utils.explain import top_factors  # noqa: E402
from utils.report import build_pdf  # noqa: E402
from utils.score import compute_heart_score  # noqa: E402

DISCLAIMER = (
    "This is an educational tool, NOT a medical device. Trained on a small "
    "1980s dataset (UCI Cleveland, 303 rows). Not clinically validated. "
    "For emergencies, seek urgent care immediately."
)

MODEL_PATH = ROOT / "models" / "heartcare_model.joblib"
INFO_PATH = ROOT / "models" / "model_info.json"
COMP_PATH = ROOT / "models" / "model_comparison.csv"

try:
    MODEL = joblib.load(MODEL_PATH)
    MODEL_INFO = json.loads(INFO_PATH.read_text(encoding="utf-8"))
except Exception as exc:  # fail fast with a clear message
    raise RuntimeError(f"Model artifacts missing under {ROOT / 'models'}: {exc}")

FEATURES: list = MODEL_INFO["features"]

app = FastAPI(title="HeartCare API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _row(payload: HeartInput) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "age": float(payload.age),
                "sex": float(payload.sex),
                "cp": float(payload.cp),
                "trestbps": float(payload.trestbps),
                "chol": float(payload.chol),
                "fbs": float(payload.fbs),
                "restecg": float(payload.restecg),
                "thalach": float(payload.thalach),
                "exang": float(payload.exang),
                "oldpeak": float(payload.oldpeak),
                "slope": float(payload.slope),
                "ca": float(payload.ca),
                "thal": float(payload.thal),
            }
        ],
        columns=FEATURES,
    )


def _lifestyle(payload: HeartInput) -> dict:
    return {
        "smoking": payload.smoking,
        "activity": payload.activity,
        "family_history": "Yes" if payload.family_history else "No",
        "known_bp_history": "Yes" if payload.bp_history else "No",
    }


def _vitals(payload: HeartInput) -> dict:
    return {
        "trestbps": float(payload.trestbps),
        "chol": float(payload.chol),
        "thalach": float(payload.thalach),
        "oldpeak": float(payload.oldpeak),
        "age": float(payload.age),
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "model": MODEL_INFO.get("model_name")}


@app.get("/api/model-info")
def model_info():
    comparison = []
    if COMP_PATH.exists():
        with open(COMP_PATH, newline="") as f:
            comparison = list(csv.DictReader(f))
    return {
        "model_name": MODEL_INFO.get("model_name"),
        "metrics": MODEL_INFO.get("metrics"),
        "features": FEATURES,
        "dataset": MODEL_INFO.get("dataset"),
        "comparison": comparison,
        "disclaimer": DISCLAIMER,
    }


@app.get("/api/demos")
def demos():
    return {"healthy": HEALTHY_DEMO, "at_risk": AT_RISK_DEMO}


@app.post("/api/score", response_model=ScoreResponse)
def score(payload: HeartInput):
    row = _row(payload)
    try:
        proba = float(MODEL.predict_proba(row)[0][list(MODEL.classes_).index(1)])
        pred = int(MODEL.predict(row)[0])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}")
    s = compute_heart_score(proba, _lifestyle(payload), _vitals(payload))
    factors = top_factors(MODEL, row, top_k=3)
    return ScoreResponse(
        score=s["score"],
        grade=s["grade"],
        label=s["label"],
        color=s["color"],
        bg=s["bg"],
        advice=s["advice"],
        model_proba=proba,
        prediction=pred,
        breakdown=s["breakdown"],
        reasons=s["reasons"],
        factors=factors,
        disclaimer=DISCLAIMER,
    )


@app.post("/api/report")
def report(payload: HeartInput):
    row = _row(payload)
    proba = float(MODEL.predict_proba(row)[0][list(MODEL.classes_).index(1)])
    pred = int(MODEL.predict(row)[0])
    s = compute_heart_score(proba, _lifestyle(payload), _vitals(payload))
    factors = top_factors(MODEL, row, top_k=3)
    pdf = build_pdf(
        s,
        proba,
        pred,
        row.to_dict("records")[0],
        _lifestyle(payload),
        payload.mode,
        factors,
        patient_name=payload.patient_name,
    )
    return StreamingResponse(
        iter([pdf]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=heartcare_report.pdf"},
    )
