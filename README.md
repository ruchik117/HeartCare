# HeartCare ❤️

Heart-health assessment and education app. Enter clinical measurements, get a
**0–100 score with an A+ to F grade**, see what raised or lowered it, and download
a PDF report. **Educational only — not a medical device.**

## Features

- Health test with Quick (7 fields) and Clinical (13 fields) modes
- Score gauge, grade badge, breakdown bars, and top reasons behind every result
- One-click healthy / at-risk demo presets (great for classroom demos)
- Downloadable PDF report, dark mode, works on phones

## Run it — Linux

**Simple version (Streamlit, Python only):**

```bash
cd HeartCare
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501**. (The trained model is already in `models/`, so no
training step is needed. To retrain from scratch: `python train_model.py`.)

**Full version (FastAPI backend + Next.js website):**

```bash
cd HeartCare
source .venv/bin/activate
pip install -r heartcare-web/requirements-api.txt
cd heartcare-web
bash run.sh
```

Website at **http://localhost:3000**, API docs at **http://localhost:8001/docs**.

## Run it — Windows

**Simple version:**

```bat
cd HeartCare
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501**.

**Full version:** install [Node.js](https://nodejs.org) once, then double-click
(or run) **`heartcare-web\run.bat`** — it starts the backend and the website
(**http://localhost:3000**) for you. Needs `..\\.venv` with the API
requirements installed:

```bat
cd HeartCare
py -m venv .venv
.venv\Scripts\activate
pip install -r heartcare-web\requirements-api.txt
```

## Try it in 30 seconds

1. Open the app and go to **Health Test**
2. Click **Fill at-risk demo** (or healthy demo), then **See my score**
3. Or open **http://localhost:3000/results?demo=at_risk** directly

## Project layout

- `app.py` — Streamlit app (simple version)
- `train_model.py` — trains and compares the models, saves to `models/`
- `utils/` — score formula, explanations, PDF reports, demo presets
- `data/` — UCI Cleveland heart-disease dataset (303 records)
- `heartcare-web/api/` — FastAPI backend
- `heartcare-web/web/` — Next.js website

## Tech stack

Python (scikit-learn, FastAPI), TypeScript (Next.js, React, Tailwind),
Plotly/Recharts for charts, fpdf2 for PDF reports.

## Disclaimer

Student project for learning. Trained on a small 1980s public dataset
(UCI Cleveland, 303 rows), not clinically validated. Never use it for
diagnosis or treatment decisions — in an emergency, seek urgent care.
