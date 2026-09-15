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

    def _extract_risk_factors(self, raw: Dict[str, Any]) -> List[Dict[str, str]]:
        factors = []
        contract = str(raw.get("Contract", ""))
        tenure = int(raw.get("tenure", 0))
        monthly = float(raw.get("MonthlyCharges", 0.0))
        tech_support = str(raw.get("TechSupport", ""))
        pay_method = str(raw.get("PaymentMethod", ""))
        internet_svc = str(raw.get("InternetService", ""))

        if contract == "Month-to-month":
            factors.append({"factor": "Contract Type", "impact": "High Risk Driver", "detail": "Customer is on a Month-to-month plan with no long-term commitment."})
        elif contract in ["One year", "Two year"]:
            factors.append({"factor": "Contract Type", "impact": "Retention Anchor", "detail": f"Signed under a {contract} contract which significantly lowers churn."})

        if tenure <= 6:
            factors.append({"factor": "Short Tenure", "impact": "High Risk Driver", "detail": f"Active for only {tenure} month(s); onboarding phase has peak churn risk."})
        elif tenure >= 24:
            factors.append({"factor": "Long-term Tenure", "impact": "Loyalty Indicator", "detail": f"Established customer with {tenure} months of continuous account history."})

        if internet_svc == "Fiber optic" and tech_support == "No":
            factors.append({"factor": "Unsupported High-Speed Service", "impact": "Friction Point", "detail": "Customer has Fiber optic internet without Tech Support add-ons."})

        if monthly > 80:
            factors.append({"factor": "Above Average Monthly Cost", "impact": "Price Sensitivity", "detail": f"Monthly billing of ${monthly:.2f} places customer in high-cost tier."})

        if pay_method == "Electronic check":
            factors.append({"factor": "Payment Method", "impact": "Behavioral Risk", "detail": "Manual Electronic check payers churn 2.5x more often than automated payers."})

        return factors

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

        risk_factors = self._extract_risk_factors(raw_customer)

        return {
            "churn_prediction": "Yes" if churn_pred == 1 else "No",
            "churn_code": churn_pred,
            "churn_probability": round(churn_prob * 100, 1),
            "retention_probability": round((1.0 - churn_prob) * 100, 1),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_factors": risk_factors,
            "metrics": self.metrics
        }
