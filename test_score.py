import sys

sys.path.insert(0, ".")
from utils.score import compute_heart_score, grade_for_score


def test_grades():
    assert grade_for_score(95)["grade"] == "A+"
    assert grade_for_score(82)["grade"] == "A"
    assert grade_for_score(75)["grade"] == "B"
    assert grade_for_score(62)["grade"] == "C"
    assert grade_for_score(51)["grade"] == "D"
    assert grade_for_score(20)["grade"] == "F"


def test_healthy_scores_high():
    s = compute_heart_score(
        0.1,
        {
            "smoking": "Never",
            "activity": "High",
            "family_history": "No",
            "known_bp_history": "No",
        },
        {"trestbps": 118, "chol": 185, "thalach": 172, "oldpeak": 0.4, "age": 32},
    )
    assert s["score"] >= 80, s


def test_atrisk_scores_low():
    s = compute_heart_score(
        0.85,
        {
            "smoking": "Current",
            "activity": "Low",
            "family_history": "Yes",
            "known_bp_history": "Yes",
        },
        {"trestbps": 152, "chol": 289, "thalach": 112, "oldpeak": 2.8, "age": 58},
    )
    assert s["score"] < 60, s


def test_breakdown_keys():
    s = compute_heart_score(
        0.5, {}, {"trestbps": 120, "chol": 200, "thalach": 150, "oldpeak": 1.0}
    )
    assert set(s["breakdown"]) == {"model", "lifestyle", "vitals"}
    assert 0 <= s["score"] <= 100


def test_pipeline_predict():
    import pandas as pd, joblib

    m = joblib.load("models/heartcare_model.joblib")
    import json

    feats = json.load(open("models/model_info.json"))["features"]
    row = pd.DataFrame([{f: 0.0 for f in feats}], columns=feats)
    # just checks shape handling, not values
    assert m.predict(row).shape == (1,)


def test_explain_top_factors():
    import pandas as pd, joblib, json
    from utils.explain import top_factors

    m = joblib.load("models/heartcare_model.joblib")
    feats = json.load(open("models/model_info.json"))["features"]
    row = pd.DataFrame([{f: 50.0 for f in feats}], columns=feats)
    f = top_factors(m, row)
    assert len(f) == 3
    assert all("friendly" in x and "direction" in x for x in f)


def test_pdf_builds():
    from utils.report import build_pdf

    s = {
        "score": 82,
        "grade": "A",
        "label": "Good",
        "advice": "Nice",
        "breakdown": {"model": 10, "lifestyle": 5, "vitals": 3},
        "reasons": ["Test reason"],
    }
    pdf = build_pdf(s, 0.3, 0, {"age": 40}, {"smoking": "Never"}, "Quick", [])
    assert pdf[:4] == b"%PDF"
