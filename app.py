import json
from pathlib import Path
from io import BytesIO

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.score import compute_heart_score
from utils.demo import HEALTHY_DEMO, AT_RISK_DEMO
from utils.explain import top_factors
from utils.report import build_pdf

st.set_page_config(
    page_title="HeartCare | Know your heart",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "heartcare_model.joblib"
INFO_PATH = BASE_DIR / "models" / "model_info.json"
COMPARISON_PATH = BASE_DIR / "models" / "model_comparison.csv"

# ---------- design system ----------
# Distinct editorial-medical: Fraunces display + Inter body,
# paper #F6F8FA, ink navy #0B1E3A, arterial coral accent, teal action.
# One memorable element: animated ECG line. Everything else quiet.

st.markdown(
    """
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
.stApp { background: #F6F8FA; font-family: 'Inter', system-ui, sans-serif; }
[data-testid="stHeader"] { background: #F6F8FA; }
.block-container { max-width: 1180px; padding-top: 1.2rem; padding-bottom: 3rem; }
h1, h2, h3 { color: #0B1E3A !important; letter-spacing: -0.02em; }
.display { font-family: 'Fraunces', serif; font-weight: 700; letter-spacing: -0.03em; }

.topbar { display:flex; align-items:center; justify-content:space-between;
  background: #0B1E3A; color: #fff; border-radius: 18px; padding: 16px 22px; margin-bottom: 18px; }
.topbar .brand { display:flex; gap:12px; align-items:center; }
.topbar .brand-mark { width:42px; height:42px; border-radius:12px; background:#FF4D5E;
  display:flex; align-items:center; justify-content:center; font-size:22px; }
.topbar .brand-name { font-family:'Fraunces',serif; font-size:22px; font-weight:700; }
.topbar .brand-sub { font-size:12.5px; color:#B9C6DA; margin-top:-2px; }
.topbar .pill { background:#13294B; border:1px solid #243A5E; color:#D7E3F4;
  font-size:12.5px; padding:7px 12px; border-radius:999px; }

.hero { background:#fff; border:1px solid #E4EAF2; border-radius:22px; padding:30px 30px 26px;
  margin-bottom:18px; position:relative; overflow:hidden; }
.hero h1 { font-family:'Fraunces',serif; font-size:44px; line-height:1.02; margin:6px 0 10px; }
.hero p { color:#475569; font-size:16px; line-height:1.65; max-width:62ch; }
.ecg { width:100%; height:64px; margin:8px 0 4px; }
.ecg path { fill:none; stroke:#FF4D5E; stroke-width:3; stroke-linecap:round; stroke-linejoin:round;
  stroke-dasharray: 600; stroke-dashoffset: 600; animation: draw 2.2s ease forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
@media (prefers-reduced-motion: reduce) { .ecg path { animation:none; stroke-dashoffset:0; } }

.card { background:#fff; border:1px solid #E4EAF2; border-radius:18px; padding:20px 20px; }
.card h3 { margin:0 0 6px; font-size:18px; }
.card p { color:#475569; font-size:14.5px; line-height:1.6; margin:0; }
.card .icon { width:40px; height:40px; border-radius:12px; display:flex; align-items:center;
  justify-content:center; font-size:20px; margin-bottom:10px; }

.grade-badge { border-radius:20px; padding:26px 24px; text-align:center; border:1px solid;
  margin-bottom:8px; }
.grade-badge .g { font-family:'Fraunces',serif; font-size:64px; line-height:1; font-weight:700; }
.grade-badge .lbl { font-weight:700; font-size:17px; margin-top:6px; }
.grade-badge .score { font-size:13px; opacity:.85; margin-top:4px; }

div.stButton > button[kind="primary"] { background:#0E9384; border:none; border-radius:12px;
  min-height:46px; font-weight:700; }
div.stButton > button[kind="primary"]:hover { background:#0B7A6E; border:none; }
div.stButton > button[kind="secondary"] { border-radius:12px; }

section[data-testid="stRadio"] div[role="radiogroup"] { gap:8px; }
section[data-testid="stRadio"] label { background:#fff; border:1px solid #E4EAF2 !important;
  border-radius:999px !important; padding:8px 18px !important; font-weight:600; color:#0B1E3A; }

.break-row { display:flex; gap:10px; margin-top:10px; }
.break { flex:1; background:#fff; border:1px solid #E4EAF2; border-radius:14px; padding:12px; text-align:center; }
.break b { display:block; font-size:20px; color:#0B1E3A; }
.break span { font-size:12px; color:#64748b; }
.reason { background:#FFF7ED; border:1px solid #FDBA74; border-radius:12px; padding:10px 12px;
  font-size:14px; margin-bottom:8px; color:#7C2D12; }
footer { visibility:hidden; }
:focus-visible { outline: 3px solid #0E9384 !important; outline-offset:2px; }
@media (max-width: 700px){ .hero h1{ font-size:32px; } .topbar{ flex-direction:column; gap:10px; align-items:flex-start;} }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_info():
    with open(INFO_PATH, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_comp():
    if COMPARISON_PATH.exists():
        return pd.read_csv(COMPARISON_PATH)
    return pd.DataFrame()


try:
    model = load_model()
    model_info = load_info()
    comp_df = load_comp()
except Exception as e:
    st.error("Model files missing. Run `python train_model.py` first.")
    st.code(str(e))
    st.stop()

# ---------- header ----------
st.markdown(
    """
<div class="topbar">
  <div class="brand">
    <div class="brand-mark">❤️</div>
    <div><div class="brand-name">HeartCare</div>
    <div class="brand-sub">Understand your heart, in plain language</div></div>
  </div>
  <div class="pill">Student project · Educational only · Not a diagnosis</div>
</div>
""",
    unsafe_allow_html=True,
)

pages = ["Home", "About", "Health Test", "Heart Health Tips"]
req = st.session_state.pop("page_req", "Home")
page = st.radio(
    "Nav",
    pages,
    index=pages.index(req) if req in pages else 0,
    horizontal=True,
    label_visibility="collapsed",
)
st.write("")

SEX_MAP = {"Female": 0, "Male": 1}
CP_MAP = {
    "Typical angina": 1,
    "Atypical angina": 2,
    "Non-anginal pain": 3,
    "Asymptomatic": 4,
}
FBS_MAP = {"No": 0, "Yes": 1}
REST_MAP = {"Normal": 0, "ST-T wave abnormality": 1, "Left ventricular hypertrophy": 2}
EXANG_MAP = {"No": 0, "Yes": 1}
SLOPE_MAP = {"Upsloping": 1, "Flat": 2, "Downsloping": 3}
THAL_MAP = {"Normal": 3, "Fixed defect": 6, "Reversible defect": 7}


def gauge_fig(score, color):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"font": {"size": 44, "color": "#0B1E3A"}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "#EDF2F7",
                "steps": [
                    {"range": [0, 50], "color": "#FEE2E2"},
                    {"range": [50, 70], "color": "#FFEDD5"},
                    {"range": [70, 85], "color": "#FEF9C3"},
                    {"range": [85, 100], "color": "#DCFCE7"},
                ],
                "threshold": {"line": {"color": "#0B1E3A", "width": 3}, "value": score},
            },
        )
    )
    fig.update_layout(
        height=250, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


# ================= HOME =================
if page == "Home":
    st.markdown(
        """
    <div class="hero">
      <svg class="ecg" viewBox="0 0 600 64" aria-hidden="true">
        <path d="M0 32 H140 L155 32 L165 10 L178 54 L190 24 L198 32 H260 L272 32 L282 14 L294 50 L306 32 H420 L432 32 L442 18 L452 46 L462 32 H600"/>
      </svg>
      <h1>Know your heart,<br/>without the jargon.</h1>
      <p>Answer a guided check, get a clear <b>score from 0–100 with a grade from A+ to F</b>,
      see what lifted or lowered it, and leave with habits worth discussing with a clinician.
      Built on the public UCI Cleveland dataset (303 records) for classroom learning.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="card"><div class="icon" style="background:#D9F2E6">🩺</div><h3>Guided check</h3><p>Quick mode needs 7 numbers. Clinical mode unlocks all 13 model features.</p></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="card"><div class="icon" style="background:#FEE2E2">📊</div><h3>Score, not scare</h3><p>One grade badge with color, a gauge, and the top reasons behind it.</p></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="card"><div class="icon" style="background:#FEF9C3">🌿</div><h3>Next steps</h3><p>Habits and check-up prompts tailored to your answers.</p></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.subheader("How it works")
    st.markdown(
        "Answer → model estimates a pattern → penalties for lifestyle and vitals shape a 0–100 score → you get a grade and reasons. Nothing here diagnoses you."
    )
    if st.button("Start health check", type="primary"):
        st.session_state["page_req"] = "Health Test"
        st.rerun()

    st.write("")
    st.subheader("Model behind the score")
    m = model_info.get("metrics", {})
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Accuracy",
        f"{m.get('Accuracy', 0):.1%}"
        if isinstance(m.get("Accuracy"), float) and m.get("Accuracy") < 1.5
        else m.get("Accuracy", "–"),
    )
    k2.metric("Precision", str(m.get("Precision", "–")))
    k3.metric("Recall", str(m.get("Recall", "–")))
    k4.metric("F1", str(m.get("F1 Score", "–")))
    if not comp_df.empty:
        fig = px.bar(
            comp_df,
            x="Model",
            y="F1 Score",
            color="Model",
            title="F1 comparison (higher is better)",
            text="F1 Score",
        )
        fig.update_layout(
            showlegend=False,
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Selected model: {model_info.get('model_name', '–')} · 80/20 stratified split · educational, not clinically validated."
    )

# ================= ABOUT =================
elif page == "About":
    st.markdown('<h1 class="display">About HeartCare</h1>', unsafe_allow_html=True)
    st.write(
        "A student ML project showing how a classifier learns patterns from clinical measurements — and how to present them responsibly."
    )
    a, b = st.columns(2)
    with a:
        st.markdown(
            '<div class="card"><h3>What it teaches</h3><p>Preprocessing with ColumnTransformer, comparing Logistic Regression / Decision Tree / Random Forest by F1, calibration limits, and why n=303 is too small for clinical use.</p></div>',
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            '<div class="card"><h3>What it is not</h3><p>Not a medical device. No severity staging, no future-risk prediction, no emergency triage. Chest pain or breathlessness → seek urgent care.</p></div>',
            unsafe_allow_html=True,
        )
    st.subheader("Dataset")
    st.write(
        "UCI Cleveland subset, 303 rows. Target collapsed: 0 = absent, 1–4 = present. 6 rows miss `ca`/`thal` (imputed with most-frequent)."
    )
    st.markdown(
        "[Open the official UCI Heart Disease dataset](https://archive.ics.uci.edu/dataset/45/heart+disease)"
    )
    st.warning(
        "Educational only. Not clinically validated. Discuss results with a professional."
    )

# ================= HEALTH TEST =================
elif page == "Health Test":
    st.markdown('<h1 class="display">Heart health check</h1>', unsafe_allow_html=True)
    st.write(
        "Pick a mode. Quick needs fewer lab values and fills safe defaults. Clinical uses all 13 model features."
    )

    mode = (
        st.segmented_control("Mode", ["Quick", "Clinical"], default="Quick")
        if hasattr(st, "segmented_control")
        else st.radio("Mode", ["Quick", "Clinical"], horizontal=True)
    )

    d1, d2, _ = st.columns([1, 1, 2])
    with d1:
        if st.button("Fill healthy demo"):
            for k, v in HEALTHY_DEMO.items():
                st.session_state[f"demo_{k}"] = v
            st.rerun()
    with d2:
        if st.button("Fill at-risk demo"):
            for k, v in AT_RISK_DEMO.items():
                st.session_state[f"demo_{k}"] = v
            st.rerun()

    def gv(key, default):
        return st.session_state.get(f"demo_{key}", default)

    with st.form("check"):
        st.subheader("Personal")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input(
                "Age (years)", 18, 100, value=gv("age", None), placeholder="e.g. 45"
            )
        with c2:
            sex_label = st.selectbox(
                "Sex (dataset coding)",
                ["Select", "Female", "Male"],
                index=["Select", "Female", "Male"].index(gv("sex_label", "Select"))
                if gv("sex_label", "Select") in ["Select", "Female", "Male"]
                else 0,
            )
        st.subheader("Vitals you likely know")
        c1, c2 = st.columns(2)
        with c1:
            cp_label = st.selectbox(
                "Chest pain category",
                [
                    "Select",
                    "Typical angina",
                    "Atypical angina",
                    "Non-anginal pain",
                    "Asymptomatic",
                ],
                index=[
                    "Select",
                    "Typical angina",
                    "Atypical angina",
                    "Non-anginal pain",
                    "Asymptomatic",
                ].index(gv("cp_label", "Select"))
                if gv("cp_label", "Select") != "Select"
                else 0,
            )
            trestbps = st.number_input(
                "Resting BP (mm Hg)",
                50,
                260,
                value=gv("trestbps", None),
                placeholder="e.g. 120",
            )
            chol = st.number_input(
                "Cholesterol (mg/dL)",
                50,
                700,
                value=gv("chol", None),
                placeholder="e.g. 200",
            )
        with c2:
            thalach = st.number_input(
                "Max heart rate (exercise)",
                50,
                250,
                value=gv("thalach", None),
                placeholder="e.g. 150",
            )
            exang_label = st.selectbox(
                "Exercise-induced angina?",
                ["Select", "No", "Yes"],
                index=["Select", "No", "Yes"].index(gv("exang_label", "Select"))
                if gv("exang_label", "Select") in ["Select", "No", "Yes"]
                else 0,
            )
            smoking = st.selectbox(
                "Smoking",
                ["Not provided", "Never", "Former", "Current"],
                index=["Not provided", "Never", "Former", "Current"].index(
                    gv("smoking", "Not provided")
                ),
            )
        if mode == "Clinical":
            st.subheader("Clinical (from reports only — don't guess)")
            c1, c2 = st.columns(2)
            with c1:
                fbs_label = st.selectbox(
                    "Fasting sugar >120?",
                    ["Select", "No", "Yes"],
                    index=["Select", "No", "Yes"].index(gv("fbs_label", "Select"))
                    if gv("fbs_label", "Select") in ["Select", "No", "Yes"]
                    else 0,
                )
                restecg_label = st.selectbox(
                    "Resting ECG",
                    [
                        "Select",
                        "Normal",
                        "ST-T wave abnormality",
                        "Left ventricular hypertrophy",
                    ],
                    index=[
                        "Select",
                        "Normal",
                        "ST-T wave abnormality",
                        "Left ventricular hypertrophy",
                    ].index(gv("restecg_label", "Select"))
                    if gv("restecg_label", "Select") != "Select"
                    else 0,
                )
                ca_label = st.selectbox(
                    "Vessels (fluoroscopy)",
                    ["Select", "0", "1", "2", "3"],
                    index=["Select", "0", "1", "2", "3"].index(gv("ca_label", "Select"))
                    if gv("ca_label", "Select") in ["Select", "0", "1", "2", "3"]
                    else 0,
                )
            with c2:
                oldpeak = st.number_input(
                    "ST depression", 0.0, 10.0, value=gv("oldpeak", None), step=0.1
                )
                slope_label = st.selectbox(
                    "ST slope",
                    ["Select", "Upsloping", "Flat", "Downsloping"],
                    index=["Select", "Upsloping", "Flat", "Downsloping"].index(
                        gv("slope_label", "Select")
                    )
                    if gv("slope_label", "Select") != "Select"
                    else 0,
                )
                thal_label = st.selectbox(
                    "Thal result",
                    ["Select", "Normal", "Fixed defect", "Reversible defect"],
                    index=[
                        "Select",
                        "Normal",
                        "Fixed defect",
                        "Reversible defect",
                    ].index(gv("thal_label", "Select"))
                    if gv("thal_label", "Select") != "Select"
                    else 0,
                )
            c1b, c2b = st.columns(2)
            with c1b:
                activity = st.selectbox(
                    "Activity",
                    ["Not provided", "Low", "Moderate", "High"],
                    index=["Not provided", "Low", "Moderate", "High"].index(
                        gv("activity", "Not provided")
                    ),
                )
            with c2b:
                family_history = st.selectbox(
                    "Family history",
                    ["Not provided", "No", "Yes", "Unsure"],
                    index=["Not provided", "No", "Yes", "Unsure"].index(
                        gv("family_history", "Not provided")
                    ),
                )
                known_bp_history = st.selectbox(
                    "BP history",
                    ["Not provided", "No", "Yes", "Unsure"],
                    index=["Not provided", "No", "Yes", "Unsure"].index(
                        gv("known_bp_history", "Not provided")
                    ),
                )
        else:
            # quick defaults
            fbs_label, restecg_label, ca_label = "No", "Normal", "0"
            oldpeak, slope_label, thal_label = 0.8, "Flat", "Normal"
            activity = st.selectbox(
                "Activity",
                ["Not provided", "Low", "Moderate", "High"],
                index=["Not provided", "Low", "Moderate", "High"].index(
                    gv("activity", "Not provided")
                ),
            )
            family_history = st.selectbox(
                "Family history", ["Not provided", "No", "Yes", "Unsure"]
            )
            known_bp_history = st.selectbox(
                "BP history", ["Not provided", "No", "Yes", "Unsure"]
            )
            st.caption(
                "Quick mode fills ECG / ST / vessels / thal with neutral defaults and tells you. Switch to Clinical if you have lab reports."
            )

        go_btn = st.form_submit_button(
            "See my score", type="primary", use_container_width=True
        )

    if go_btn:
        missing = []
        for lbl, v in {
            "Age": age,
            "Resting BP": trestbps,
            "Cholesterol": chol,
            "Max heart rate": thalach,
        }.items():
            if v is None:
                missing.append(lbl)
        for lbl, v in {
            "Sex": sex_label,
            "Chest pain": cp_label,
            "Angina": exang_label,
        }.items():
            if v == "Select":
                missing.append(lbl)
        if mode == "Clinical":
            for lbl, v in {
                "Fasting sugar": fbs_label,
                "ECG": restecg_label,
                "ST slope": slope_label,
                "Vessels": ca_label,
                "Thal": thal_label,
            }.items():
                if v == "Select":
                    missing.append(lbl)
            if oldpeak is None:
                missing.append("ST depression")
        if missing:
            st.error("Missing: " + ", ".join(missing))
        else:
            problems = []
            if not 18 <= age <= 100:
                problems.append("Age must be 18–100.")
            if not 80 <= trestbps <= 250:
                problems.append("Check BP value (expected 80–250).")
            if not 80 <= chol <= 600:
                problems.append("Check cholesterol (expected 80–600).")
            if not 60 <= thalach <= 220:
                problems.append("Check max heart rate (expected 60–220).")
            if problems:
                for p in problems:
                    st.error(p)
            else:
                row = pd.DataFrame(
                    [
                        {
                            "age": float(age),
                            "sex": float(SEX_MAP[sex_label]),
                            "cp": float(CP_MAP[cp_label]),
                            "trestbps": float(trestbps),
                            "chol": float(chol),
                            "fbs": float(FBS_MAP[fbs_label]),
                            "restecg": float(REST_MAP[restecg_label]),
                            "thalach": float(thalach),
                            "exang": float(EXANG_MAP[exang_label]),
                            "oldpeak": float(oldpeak),
                            "slope": float(SLOPE_MAP[slope_label]),
                            "ca": float(ca_label),
                            "thal": float(THAL_MAP[thal_label]),
                        }
                    ],
                    columns=model_info["features"],
                )
                try:
                    pred = int(model.predict(row)[0])
                    proba = float(
                        model.predict_proba(row)[0][list(model.classes_).index(1)]
                    )
                    life = {
                        "smoking": smoking,
                        "activity": activity,
                        "family_history": family_history,
                        "known_bp_history": known_bp_history,
                    }
                    vit = {
                        "trestbps": float(trestbps),
                        "chol": float(chol),
                        "thalach": float(thalach),
                        "oldpeak": float(oldpeak),
                        "age": float(age),
                    }
                    score = compute_heart_score(proba, life, vit)
                    factors = top_factors(model, row, top_k=3)
                    st.session_state["result"] = {
                        "pred": pred,
                        "proba": proba,
                        "score": score,
                        "factors": factors,
                        "inputs": row.to_dict("records")[0],
                        "life": life,
                        "mode": mode,
                    }
                    st.success("Done — see your score below.")
                except Exception as e:
                    st.error("Could not score. Retrain model?")
                    st.code(str(e))

    r = st.session_state.get("result")
    if r:
        st.divider()
        s = r["score"]
        st.markdown('<h2 class="display">Your result</h2>', unsafe_allow_html=True)
        left, right = st.columns([1, 1])
        with left:
            st.markdown(
                f"""<div class="grade-badge" style="background:{s["bg"]}; border-color:{s["color"]}; color:{s["color"]}">
              <div class="g">{s["grade"]}</div><div class="lbl">{s["label"]} · {s["score"]}/100</div>
              <div class="score">Model pattern {r["proba"]:.0%} · {r["mode"]} mode · {s["advice"]}</div></div>""",
                unsafe_allow_html=True,
            )
            st.caption(
                "Educational score only. Not a diagnosis or future-risk prediction."
            )
        with right:
            st.plotly_chart(gauge_fig(s["score"], s["color"]), use_container_width=True)
        st.subheader("What shaped your score")
        b = s["breakdown"]
        st.markdown(
            f"""<div class="break-row"><div class="break"><b>-{b["model"]}</b><span>Model pattern</span></div>
        <div class="break"><b>-{b["lifestyle"]}</b><span>Lifestyle</span></div>
        <div class="break"><b>-{b["vitals"]}</b><span>Vitals</span></div></div>""",
            unsafe_allow_html=True,
        )
        st.write("")
        for reason in s["reasons"]:
            st.markdown(f'<div class="reason">⚠️ {reason}</div>', unsafe_allow_html=True)

        factors = r.get("factors", [])
        if factors:
            st.subheader("Why the model thinks so")
            st.caption(
                "SHAP-style: input value × learned weight, grouped back to original fields. Positive pushes toward disease pattern."
            )
            fdf = pd.DataFrame(factors)
            fig2 = px.bar(
                fdf,
                x="impact",
                y="friendly",
                orientation="h",
                color="direction",
                color_discrete_map={
                    "raising": "#EF4444",
                    "lowering": "#16A34A",
                    "neutral": "#94A3B8",
                },
                title="Top model factors",
            )
            fig2.update_layout(
                height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig2, use_container_width=True)
            for f in factors:
                arrow = (
                    "🔺 raising"
                    if f["direction"] == "raising"
                    else (
                        "🟢 lowering" if f["direction"] == "lowering" else "➖ neutral"
                    )
                )
                st.markdown(
                    f'<div class="card" style="margin-bottom:8px"><b>{f["friendly"]}</b> — {arrow} (impact {f["impact"]})<br/><span style="color:#475569;font-size:13px">{f["hint"]}</span></div>',
                    unsafe_allow_html=True,
                )
        st.subheader("Your numbers")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Age": f"{r['inputs']['age']:.0f} y",
                        "BP": f"{r['inputs']['trestbps']:.0f} mmHg",
                        "Chol": f"{r['inputs']['chol']:.0f} mg/dL",
                        "Max HR": f"{r['inputs']['thalach']:.0f}",
                        "ST": f"{r['inputs']['oldpeak']:.1f}",
                    }
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )
        # download
        out = pd.DataFrame(
            [
                {
                    "score": s["score"],
                    "grade": s["grade"],
                    "proba": r["proba"],
                    **r["inputs"],
                }
            ]
        )
        st.download_button(
            "Download result (CSV)",
            out.to_csv(index=False),
            "heartcare_result.csv",
            "text/csv",
        )
        try:
            pdf_bytes = build_pdf(
                s,
                r["proba"],
                r["pred"],
                r["inputs"],
                r["life"],
                r["mode"],
                r.get("factors", []),
            )
            st.download_button(
                "Download report (PDF)",
                pdf_bytes,
                "heartcare_report.pdf",
                "application/pdf",
            )
        except Exception as e:
            st.caption(f"PDF unavailable: {e}")
        if st.button("Clear"):
            st.session_state.pop("result", None)
            st.rerun()
        st.warning(
            "Small 1980s dataset, not validated. Don't use for treatment decisions."
        )

# ================= TIPS =================
else:
    st.markdown('<h1 class="display">Everyday habits</h1>', unsafe_allow_html=True)
    tips = [
        (
            "🥗 Eat balanced",
            "Vegetables, fruit, whole grains. Less salt and ultra-processed food.",
        ),
        (
            "🚶 Move often",
            "Pick activity that fits your health. Consistency beats intensity.",
        ),
        ("🚭 Avoid tobacco", "No smoking or chewing tobacco. Ask for help quitting."),
        ("🩺 Get checked", "Track BP and cholesterol as your clinician advises."),
        ("😴 Sleep steady", "Regular schedule. Flag snoring or gasping to a doctor."),
        ("🧘 Ease stress", "Walk, breathe, connect. Small routines help."),
    ]
    for t, d in tips:
        with st.container(border=True):
            st.subheader(t)
            st.write(d)
    st.error(
        "Chest pain, severe breathlessness, fainting? Get urgent care now — not this website."
    )

st.divider()
st.markdown(
    '<div style="text-align:center;color:#64748b;font-size:13px"><b>HeartCare</b> · classroom ML · not a medical device</div>',
    unsafe_allow_html=True,
)
