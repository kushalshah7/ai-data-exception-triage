from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import MODELS_DIR, PROCESSED_DIR, RANDOM_SEED
from src.feature_engineering import FEATURE_COLUMNS, build_exception_features, model_matrix

CATEGORICAL = ["domain", "source_system", "region", "asset_class"]
NUMERIC = [c for c in FEATURE_COLUMNS if c not in CATEGORICAL]


def train() -> dict[str, float]:
    df = build_exception_features()
    X, y = model_matrix(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=RANDOM_SEED)
    preprocessor = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", StandardScaler(), NUMERIC),
        ]
    )
    baseline = Pipeline([("prep", preprocessor), ("model", LogisticRegression(max_iter=1000, class_weight="balanced"))])
    improved = Pipeline(
        [
            ("prep", preprocessor),
            ("model", RandomForestClassifier(n_estimators=240, min_samples_leaf=3, class_weight="balanced", random_state=RANDOM_SEED)),
        ]
    )
    baseline.fit(X_train, y_train)
    improved.fit(X_train, y_train)
    pred = improved.predict(X_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "macro_f1": round(float(f1_score(y_test, pred, average="macro")), 4),
        "model_version": "rf_triage_v1",
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(improved, MODELS_DIR / "exception_classifier.joblib")
    joblib.dump(baseline, MODELS_DIR / "owner_recommender.joblib")
    report = pd.DataFrame(classification_report(y_test, pred, output_dict=True)).T.reset_index(names="class")
    report.to_csv(PROCESSED_DIR / "model_metrics.csv", index=False)
    labels = sorted(y.unique())
    pd.DataFrame(confusion_matrix(y_test, pred, labels=labels), index=labels, columns=labels).to_csv(PROCESSED_DIR / "confusion_matrix.csv")
    (PROCESSED_DIR / "model_summary.json").write_text(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    print(train())
