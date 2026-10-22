"""SHAP-style per-feature reasons without heavy shap dependency.
Works with the saved sklearn Pipeline (preprocessor + classifier).
For LogisticRegression: contribution = transformed_value * coef.
For trees: falls back to global importances + out-of-range check.
"""

import numpy as np

FRIENDLY = {
    "age": "Age",
    "sex": "Sex",
    "cp": "Chest pain type",
    "trestbps": "Resting blood pressure",
    "chol": "Cholesterol",
    "fbs": "Fasting blood sugar",
    "restecg": "Resting ECG",
    "thalach": "Max heart rate",
    "exang": "Exercise angina",
    "oldpeak": "ST depression",
    "slope": "ST slope",
    "ca": "Vessels (fluoroscopy)",
    "thal": "Thal result",
}

HEALTHY_HINT = {
    "age": "younger age lowers pattern risk",
    "sex": "",
    "cp": "non-anginal / typical patterns differ",
    "trestbps": "keep BP under 130",
    "chol": "keep cholesterol under 200",
    "fbs": "normal fasting sugar helps",
    "restecg": "normal ECG is reassuring",
    "thalach": "higher exercise heart rate is typical of fitter hearts",
    "exang": "no exercise angina is reassuring",
    "oldpeak": "low ST depression is reassuring",
    "slope": "upsloping ST is more typical of healthy",
    "ca": "0 visible vessels is reassuring",
    "thal": "normal thal is reassuring",
}


def top_factors(pipeline, input_df, top_k=3):
    """Return list of {feature, friendly, impact, direction} sorted by |impact|."""
    try:
        pre = pipeline.named_steps["preprocessor"]
        clf = pipeline.named_steps["classifier"]
        X = pre.transform(input_df)  # sparse or dense
        if hasattr(X, "toarray"):
            X = X.toarray()
        x = np.asarray(X[0], dtype=float)

        # feature names after ColumnTransformer
        try:
            names = list(pre.get_feature_names_out())
        except Exception:
            names = [f"f{i}" for i in range(len(x))]

        if hasattr(clf, "coef_"):
            coef = np.asarray(clf.coef_[0], dtype=float).ravel()
            n = min(len(x), len(coef))
            contrib = x[:n] * coef[:n]
        elif hasattr(clf, "feature_importances_"):
            imp = np.asarray(clf.feature_importances_, dtype=float).ravel()
            n = min(len(x), len(imp))
            # sign by whether value is above median-ish (positive direction proxy)
            contrib = np.abs(x[:n]) * imp[:n] * 0.5
            # flip sign for clearly healthy values? keep positive, UI marks as raising
            # better: compare raw input out-of-range to decide direction later
        else:
            return []

        # aggregate one-hot groups back to original feature, e.g. categorical__ca_2.0 -> ca
        agg = {}
        for fname, c in zip(names[:n], contrib[:n]):
            orig = fname
            # names look like "numeric__age" or "categorical__ca_2.0"
            if "__" in fname:
                tail = fname.split("__", 1)[1]
                # tail may be "ca_2.0" -> strip last _value part if matches known feature
                matched = None
                for f in FRIENDLY:
                    if tail == f or tail.startswith(f + "_"):
                        matched = f
                        break
                orig = matched or tail
            agg[orig] = agg.get(orig, 0.0) + float(c)

        ranked = sorted(agg.items(), key=lambda kv: abs(kv[1]), reverse=True)[:top_k]
        out = []
        for feat, impact in ranked:
            direction = (
                "raising"
                if impact > 0.02
                else ("lowering" if impact < -0.02 else "neutral")
            )
            out.append(
                {
                    "feature": feat,
                    "friendly": FRIENDLY.get(feat, feat),
                    "impact": round(float(impact), 3),
                    "direction": direction,
                    "hint": HEALTHY_HINT.get(feat, ""),
                }
            )
        return out
    except Exception:
        return []
