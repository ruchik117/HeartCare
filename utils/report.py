"""PDF report via fpdf2 - no extra system deps.

Content contract (do not remove): score, grade, proba, prediction, breakdown,
reasons, top factors, inputs, lifestyle, disclaimer. Layout may improve.
Patient header (name/date/mode) is additive only.
"""

from datetime import datetime

from fpdf import FPDF

INK = (11, 30, 58)
MUTED = (100, 116, 139)
LIGHT = (246, 248, 250)
LINE = (228, 234, 242)


def _hex(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class Report(FPDF):
    def section(self, title: str):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*INK)
        self.set_fill_color(*LIGHT)
        self.cell(0, 9, f"  {title}", ln=True, fill=True)
        self.ln(2)


def build_pdf(
    score: dict,
    proba: float,
    pred: int,
    inputs: dict,
    lifestyle: dict,
    mode: str,
    factors: list,
    patient_name: str | None = None,
) -> bytes:
    pdf = Report(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # header bar
    pdf.set_fill_color(*INK)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 13, "  HeartCare - Heart Health Report", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, "  Educational only - not a diagnosis", ln=True, fill=True)
    pdf.ln(4)

    # patient block
    pdf.set_text_color(*INK)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Patient details", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*MUTED)
    rows = [
        ("Name", (patient_name or "").strip() or "Not provided"),
        ("Date", datetime.now().strftime("%Y-%m-%d %H:%M")),
        (
            "Mode",
            f"{mode} (Quick fills 6 clinical fields with neutral defaults)"
            if mode == "Quick"
            else mode,
        ),
        (
            "Classification",
            f"{'positive' if pred == 1 else 'negative'} class (dataset pattern)",
        ),
    ]
    for k, v in rows:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*INK)
        pdf.cell(38, 7, f"  {k}")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 7, str(v), ln=True)
    pdf.ln(3)

    # grade block
    r, g, b = _hex(score.get("color") or "#0f172a")
    pdf.set_font("Helvetica", "B", 40)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 16, f"{score['grade']}  {score['score']}/100", ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*INK)
    pdf.cell(0, 7, f"{score['label']} - {score['advice']}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 6, f"Model positive-class probability: {proba:.0%}", ln=True)
    bd = score["breakdown"]
    pdf.cell(
        0,
        6,
        f"Deductions - model: -{bd['model']}   lifestyle: -{bd['lifestyle']}   vitals: -{bd['vitals']}",
        ln=True,
    )
    pdf.ln(3)

    pdf.section("What shaped your score")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 41, 59)
    for t in score.get("reasons", []):
        pdf.cell(0, 6.5, f"  - {t}", ln=True)

    if factors:
        pdf.ln(2)
        pdf.section("Top model factors (SHAP-style)")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 41, 59)
        for f in factors:
            pdf.cell(
                0,
                6.5,
                f"  - {f['friendly']}: {f['direction']} (impact {f['impact']}) {f.get('hint', '')}",
                ln=True,
            )

    pdf.ln(2)
    pdf.section("Your submitted measurements")
    labels = {
        "age": "Age (y)",
        "sex": "Sex (0=F,1=M)",
        "cp": "Chest pain (1-4)",
        "trestbps": "Resting BP (mmHg)",
        "chol": "Cholesterol (mg/dL)",
        "fbs": "Fasting sugar>120",
        "restecg": "Resting ECG (0-2)",
        "thalach": "Max heart rate",
        "exang": "Exercise angina",
        "oldpeak": "ST depression",
        "slope": "ST slope (1-3)",
        "ca": "Vessels (0-3)",
        "thal": "Thal (3/6/7)",
    }
    pdf.set_font("Helvetica", "", 10)
    fill = False
    for k in [
        "age",
        "sex",
        "cp",
        "trestbps",
        "chol",
        "fbs",
        "restecg",
        "thalach",
        "exang",
        "oldpeak",
        "slope",
        "ca",
        "thal",
    ]:
        v = inputs.get(k, "-")
        try:
            v = f"{float(v):g}"
        except (TypeError, ValueError):
            pass
        if fill:
            pdf.set_fill_color(*LIGHT)
        pdf.set_text_color(*INK)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(70, 6.5, f"  {labels.get(k, k)}", fill=fill)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 6.5, f"  {v}", ln=True, fill=fill)
        fill = not fill

    pdf.ln(2)
    pdf.section("Lifestyle (display only, not model inputs)")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 41, 59)
    for k, v in lifestyle.items():
        pdf.cell(0, 6.5, f"  - {k}: {v}", ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*INK)
    pdf.multi_cell(
        0,
        5.5,
        "Disclaimer: small 1980s public dataset, not clinically validated. "
        "Do not use for treatment decisions or to delay care. Chest pain, severe "
        "breathlessness, fainting - seek urgent care.",
    )
    return bytes(pdf.output())
