import os
import json
import joblib
import pandas as pd
from typing import Dict, Any, List

class ChurnPredictor:
    def __init__(self, artifacts_dir: str = None):
        if artifacts_dir is None:
            artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
        
        self.artifacts_dir = artifacts_dir
        self.model = joblib.load(os.path.join(artifacts_dir, "churn_model.pkl"))
        self.scaler = joblib.load(os.path.join(artifacts_dir, "scaler.pkl"))
        
        with open(os.path.join(artifacts_dir, "meta.json"), "r", encoding="utf-8") as f:
            self.meta = json.load(f)

        self.feature_order = self.meta["feature_order"]
        self.num_cols = self.meta["num_cols"]
        self.cat_cols = self.meta["cat_cols"]
        self.cat_mappings = self.meta["cat_mappings"]
        self.metrics = self.meta.get("metrics", {})

    def preprocess(self, data_dict: Dict[str, Any]) -> pd.DataFrame:
        row = data_dict.copy()
        tenure = int(row.get("tenure", 1))
        monthly = float(row.get("MonthlyCharges", 0.0))
        total = row.get("TotalCharges")
        row["tenure"] = tenure
        row["MonthlyCharges"] = monthly
        row["TotalCharges"] = float(total) if total is not None and str(total).strip() != "" else tenure * monthly

        encoded = {}
        for c in self.feature_order:
            if c in self.cat_cols:
                raw_val = str(row.get(c, "")).strip()
                mapping = self.cat_mappings.get(c, {})
                encoded[c] = mapping.get(raw_val, mapping.get(raw_val.capitalize(), 0))
            else:
                encoded[c] = float(row.get(c, 0.0))

        df_input = pd.DataFrame([encoded])[self.feature_order]
        df_scaled = df_input.copy()
        df_scaled[self.num_cols] = self.scaler.transform(df_input[self.num_cols])
        return df_scaled

    def predict(self, raw_customer: Dict[str, Any]) -> Dict[str, Any]:
        df_scaled = self.preprocess(raw_customer)
        churn_prob = float(self.model.predict_proba(df_scaled)[0, 1])
        churn_pred = int(churn_prob >= 0.5)

        if churn_prob >= 0.60:
            risk_level, risk_color = "High Risk", "#ef4444"
        elif churn_prob >= 0.35:
            risk_level, risk_color = "Moderate Risk", "#f59e0b"
        else:
            risk_level, risk_color = "Low Risk", "#10b981"

        return {
            "churn_prediction": "Yes" if churn_pred == 1 else "No",
            "churn_code": churn_pred,
            "churn_probability": round(churn_prob * 100, 1),
            "retention_probability": round((1.0 - churn_prob) * 100, 1),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "metrics": self.metrics
        }
