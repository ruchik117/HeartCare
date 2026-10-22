"""Parity gate: API responses must be NUMERICALLY IDENTICAL to direct ML-core calls.

If any score differs by even 0.01, stop and diagnose — do not build frontend.
Run: cd /home/paimon/COD/HeartCare && .venv/bin/python -m pytest heartcare-web/tests/test_api.py -q
"""

import sys

sys.path.insert(0, ".")
sys.path.insert(0, "heartcare-web")

from fastapi.testclient import TestClient

from api.main import app
from utils.explain import top_factors
from utils.score import compute_heart_score, grade_for_score
import joblib
import pandas as pd
import json

client = TestClient(app)

HEALTHY = {
    "age": 32,
    "sex": 0,
    "cp": 3,
    "trestbps": 118,
    "chol": 185,
    "fbs": 0,
    "restecg": 0,
    "thalach": 172,
    "exang": 0,
    "oldpeak": 0.4,
    "slope": 2,
    "ca": 0,
    "thal": 3,
    "smoking": "Never",
    "activity": "High",
    "family_history": False,
    "bp_history": False,
    "mode": "Clinical",
}
AT_RISK = {
    "age": 58,
    "sex": 1,
    "cp": 4,
    "trestbps": 152,
    "chol": 289,
    "fbs": 1,
    "restecg": 1,
    "thalach": 112,
    "exang": 1,
    "oldpeak": 2.8,
    "slope": 2,
    "ca": 2,
    "thal": 7,
    "smoking": "Current",
    "activity": "Low",
    "family_history": True,
    "bp_history": True,
    "mode": "Clinical",
}
MID = {
    "age": 45,
    "sex": 1,
    "cp": 2,
    "trestbps": 135,
    "chol": 230,
    "fbs": 0,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 1.2,
    "slope": 2,
    "ca": 0,
    "thal": 3,
    "smoking": "Former",
    "activity": "Moderate",
    "family_history": False,
    "bp_history": True,
    "mode": "Quick",
}

MODEL = joblib.load("models/heartcare_model.joblib")
FEATS = json.load(open("models/model_info.json"))["features"]


def _direct(payload):
    row = pd.DataFrame([{f: float(payload[f]) for f in FEATS}], columns=FEATS)
    proba = float(MODEL.predict_proba(row)[0][list(MODEL.classes_).index(1)])
    life = {
        "smoking": payload["smoking"],
        "activity": payload["activity"],
        "family_history": "Yes" if payload["family_history"] else "No",
        "known_bp_history": "Yes" if payload["bp_history"] else "No",
    }
    vit = {
        "trestbps": payload["trestbps"],
        "chol": payload["chol"],
        "thalach": payload["thalach"],
        "oldpeak": payload["oldpeak"],
        "age": payload["age"],
    }
    return compute_heart_score(proba, life, vit), proba, row


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_grades_match_direct():
    # mirrors test_score.py::test_grades bands through real payloads
    for p in (HEALTHY, MID, AT_RISK):
        expected, _, _ = _direct(p)
        got = client.post("/api/score", json=p).json()
        assert (
            got["grade"]
            == expected["grade"]
            == grade_for_score(expected["score"])["grade"]
        )
    assert grade_for_score(95)["grade"] == "A+"
    assert grade_for_score(20)["grade"] == "F"


def test_healthy_parity():
    expected, proba, _ = _direct(HEALTHY)
    got = client.post("/api/score", json=HEALTHY).json()
    assert got["score"] == expected["score"]  # exact, not approx
    assert abs(got["model_proba"] - proba) < 1e-12
    assert got["score"] >= 80


def test_atrisk_parity():
    expected, _, _ = _direct(AT_RISK)
    got = client.post("/api/score", json=AT_RISK).json()
    assert got["score"] == expected["score"]
    assert got["breakdown"] == expected["breakdown"]
    assert got["reasons"] == expected["reasons"]
    assert got["score"] < 60


def test_mid_parity_breakdown_keys():
    expected, _, _ = _direct(MID)
    got = client.post("/api/score", json=MID).json()
    assert got["score"] == expected["score"]
    assert set(got["breakdown"]) == {"model", "lifestyle", "vitals"}
    assert 0 <= got["score"] <= 100


def test_factors_parity():
    _, _, row = _direct(AT_RISK)
    expected = top_factors(MODEL, row)
    got = client.post("/api/score", json=AT_RISK).json()
    assert got["factors"] == expected
    assert len(got["factors"]) == 3


def test_report_with_name():
    p = dict(HEALTHY, patient_name="Test Patient")
    r = client.post("/api/report", json=p)
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"
    assert len(r.content) > 1000


def test_model_info_matches_artifacts():
    info = client.get("/api/model-info").json()
    disk = json.load(open("models/model_info.json"))
    assert info["metrics"] == disk["metrics"]
    assert info["features"] == disk["features"]
    assert len(info["comparison"]) == 3


def test_demos_present():
    d = client.get("/api/demos").json()
    assert d["healthy"]["age"] == 32 and d["at_risk"]["age"] == 58


def test_validation_boundaries():
    bad_age = dict(HEALTHY, age=0)
    assert client.post("/api/score", json=bad_age).status_code == 422
    bad_bp = dict(HEALTHY, trestbps=251)
    assert client.post("/api/score", json=bad_bp).status_code == 422
    bad_chol = dict(HEALTHY, chol=601)
    assert client.post("/api/score", json=bad_chol).status_code == 422
    bad_hr = dict(HEALTHY, thalach=49)
    assert client.post("/api/score", json=bad_hr).status_code == 422
    bad_oldpeak = dict(HEALTHY, oldpeak=10.5)
    assert client.post("/api/score", json=bad_oldpeak).status_code == 422
    ok_edge = dict(HEALTHY, age=120, trestbps=250, chol=600, thalach=250, oldpeak=10.0)
    assert client.post("/api/score", json=ok_edge).status_code == 200
