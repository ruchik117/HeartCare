"""HeartCare Score: model prob + lifestyle + vitals -> 0-100 + grade."""

GRADE_MAP = [
    (
        90,
        "A+",
        "Excellent",
        "#16a34a",
        "#dcfce7",
        "Keep up the great habits. Maintain regular check-ups.",
    ),
    (80, "A", "Good", "#15803d", "#dcfce7", "Solid. Small tweaks keep you here."),
    (
        70,
        "B",
        "Fair",
        "#a16207",
        "#fef9c3",
        "Room to improve activity, diet, or vitals.",
    ),
    (
        60,
        "C",
        "At risk",
        "#c2410c",
        "#ffedd5",
        "Talk to a clinician about your risk factors.",
    ),
    (
        50,
        "D",
        "High risk",
        "#dc2626",
        "#fee2e2",
        "Book a clinical check-up soon. Don't ignore symptoms.",
    ),
    (
        0,
        "F",
        "Critical",
        "#991b1b",
        "#fee2e2",
        "Seek prompt medical advice. This is educational only.",
    ),
]


def grade_for_score(score: float):
    for threshold, grade, label, color, bg, advice in GRADE_MAP:
        if score >= threshold:
            return {
                "grade": grade,
                "label": label,
                "color": color,
                "bg": bg,
                "advice": advice,
            }
    return {
        "grade": "F",
        "label": "Critical",
        "color": "#991b1b",
        "bg": "#fee2e2",
        "advice": "",
    }


def compute_heart_score(model_prob: float, lifestyle: dict, vitals: dict) -> dict:
    """
    model_prob: 0-1 positive class probability
    lifestyle: smoking, activity, family_history, known_bp_history
    vitals: trestbps, chol, thalach, oldpeak, age
    returns score, grade dict, breakdown, reasons list
    """
    reasons = []
    # 40% model
    model_part = 40 * float(model_prob)

    # 30% lifestyle
    life_pen = 0.0
    smoking = lifestyle.get("smoking", "Not provided")
    activity = lifestyle.get("activity", "Not provided")
    fam = lifestyle.get("family_history", "Not provided")
    bp_h = lifestyle.get("known_bp_history", "Not provided")

    if smoking == "Current":
        life_pen += 1.0
        reasons.append("Current smoking adds major risk")
    elif smoking == "Former":
        life_pen += 0.5
        reasons.append("Former smoking still counts - good job quitting")
    if activity == "Low":
        life_pen += 0.6
        reasons.append("Low physical activity")
    elif activity == "Moderate":
        life_pen += 0.3
    if fam == "Yes":
        life_pen += 0.4
        reasons.append("Family history reported")
    if bp_h == "Yes":
        life_pen += 0.5
        reasons.append("History of high blood pressure")
    life_pen = min(life_pen, 2.0)  # cap
    life_part = 15 * life_pen  # max 30

    # 30% vitals
    vit_pen = 0.0
    trestbps = vitals.get("trestbps", 120)
    chol = vitals.get("chol", 200)
    thalach = vitals.get("thalach", 150)
    oldpeak = vitals.get("oldpeak", 0.0)

    if trestbps and trestbps > 140:
        vit_pen += 0.5
        reasons.append(f"Resting BP {trestbps:.0f} above 140")
    elif trestbps and trestbps > 130:
        vit_pen += 0.25
        reasons.append(f"Resting BP {trestbps:.0f} borderline high")
    if chol and chol > 240:
        vit_pen += 0.5
        reasons.append(f"Cholesterol {chol:.0f} above 240")
    elif chol and chol > 200:
        vit_pen += 0.25
    if oldpeak and oldpeak > 2.0:
        vit_pen += 0.5
        reasons.append(f"ST depression {oldpeak:.1f} high")
    elif oldpeak and oldpeak > 1.0:
        vit_pen += 0.25
    if thalach and thalach < 100:
        vit_pen += 0.25
        reasons.append(f"Max heart rate {thalach:.0f} low")
    vit_pen = min(vit_pen, 2.0)
    vit_part = 15 * vit_pen

    score = max(0, min(100, round(100 - model_part - life_part - vit_part)))
    g = grade_for_score(score)

    breakdown = {
        "model": round(model_part, 1),
        "lifestyle": round(life_part, 1),
        "vitals": round(vit_part, 1),
    }
    if not reasons:
        reasons = ["No major risk flags in provided data"]
    return {"score": score, **g, "breakdown": breakdown, "reasons": reasons[:4]}
