"""Pydantic validation boundaries.

Ranges mirror the Streamlit form input widgets in app.py EXACTLY
(age 1-120 per spec; trestbps 50-250; chol 50-600; thalach 50-250; oldpeak 0-10).
Do not widen without updating the parity tests.
"""

from typing import Literal

from pydantic import BaseModel, Field


class HeartInput(BaseModel):
    age: int = Field(..., ge=1, le=120)
    sex: Literal[0, 1]
    cp: Literal[1, 2, 3, 4]
    trestbps: int = Field(..., ge=50, le=250)
    chol: int = Field(..., ge=50, le=600)
    fbs: Literal[0, 1]
    restecg: Literal[0, 1, 2]
    thalach: int = Field(..., ge=50, le=250)
    exang: Literal[0, 1]
    oldpeak: float = Field(..., ge=0, le=10)
    slope: Literal[1, 2, 3]
    ca: Literal[0, 1, 2, 3]
    thal: Literal[3, 6, 7]
    smoking: Literal["Never", "Former", "Current"] = "Never"
    activity: Literal["Low", "Moderate", "High"] = "Moderate"
    family_history: bool = False
    bp_history: bool = False
    mode: Literal["Quick", "Clinical"] = "Clinical"
    patient_name: str | None = Field(default=None, max_length=100)


class ScoreResponse(BaseModel):
    score: int
    grade: str
    label: str
    color: str
    bg: str
    advice: str
    model_proba: float
    prediction: int
    breakdown: dict
    reasons: list
    factors: list
    disclaimer: str
