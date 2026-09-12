import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List

class ChurnPredictor:
    def __init__(self, artifacts_dir: str = None):
        if artifacts_dir is None:
            artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
        
        self.artifacts_dir = artifacts_dir
        self.model_path = os.path.join(artifacts_dir, "churn_model.pkl")
        self.scaler_path = os.path.join(artifacts_dir, "scaler.pkl")
        self.meta_path = os.path.join(artifacts_dir, "meta.json")

        if not (os.path.exists(self.model_path) and os.path.exists(self.scaler_path) and os.path.exists(self.meta_path)):
            raise FileNotFoundError(f"Model artifacts not found in {artifacts_dir}. Please run export_model.py first.")

        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

        self.feature_order = self.meta["feature_order"]
        self.num_cols = self.meta["num_cols"]
        self.cat_cols = self.meta["cat_cols"]
        self.cat_mappings = self.meta["cat_mappings"]
        self.metrics = self.meta.get("metrics", {})

    def preprocess(self, data_dict: Dict[str, Any]) -> pd.DataFrame:
        row = data_dict.copy()

        # Handle TotalCharges if not provided or empty
        if row.get("TotalCharges") is None or str(row.get("TotalCharges")).strip() == "":
            tenure = float(row.get("tenure", 1))
            monthly = float(row.get("MonthlyCharges", 0.0))
            row["TotalCharges"] = tenure * monthly
        else:
            row["TotalCharges"] = float(row["TotalCharges"])

        row["tenure"] = int(row.get("tenure", 1))
        row["MonthlyCharges"] = float(row.get("MonthlyCharges", 0.0))

        # Standardize categorical inputs with fallbacks
        encoded_dict = {}
        for c in self.feature_order:
            if c in self.cat_cols:
                raw_val = str(row.get(c, "")).strip()
                mapping = self.cat_mappings.get(c, {})
                if raw_val in mapping:
                    encoded_dict[c] = mapping[raw_val]
                else:
                    # Find closest case-insensitive match or default to 0
                    matched = None
                    for k, v in mapping.items():
                        if k.lower() == raw_val.lower():
                            matched = v
                            break
                    encoded_dict[c] = matched if matched is not None else 0
            else:
                encoded_dict[c] = float(row.get(c, 0.0))

        df_input = pd.DataFrame([encoded_dict])[self.feature_order]

        # Apply scaling to numeric features
        df_scaled = df_input.copy()
        df_scaled[self.num_cols] = self.scaler.transform(df_input[self.num_cols])
        return df_scaled

    def predict(self, raw_customer: Dict[str, Any]) -> Dict[str, Any]:
        df_scaled = self.preprocess(raw_customer)
        churn_prob = float(self.model.predict_proba(df_scaled)[0, 1])
        churn_pred = int(churn_prob >= 0.5)

        retention_prob = 1.0 - churn_prob

        # Determine risk tier & styling
        if churn_prob >= 0.60:
            risk_level = "High Risk"
            risk_color = "#ef4444"
        elif churn_prob >= 0.35:
            risk_level = "Moderate Risk"
            risk_color = "#f59e0b"
        else:
            risk_level = "Low Risk"
            risk_color = "#10b981"

        risk_factors = self._extract_risk_factors(raw_customer, churn_prob)
        retention_strategies = self._generate_retention_strategies(raw_customer, risk_factors)

        return {
            "churn_prediction": "Yes" if churn_pred == 1 else "No",
            "churn_code": churn_pred,
            "churn_probability": round(churn_prob * 100, 1),
            "retention_probability": round(retention_prob * 100, 1),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_factors": risk_factors,
            "retention_strategies": retention_strategies,
            "metrics": self.metrics
        }

    def _extract_risk_factors(self, raw: Dict[str, Any], churn_prob: float) -> List[Dict[str, str]]:
        factors = []
        contract = str(raw.get("Contract", ""))
        tenure = int(raw.get("tenure", 0))
        monthly = float(raw.get("MonthlyCharges", 0.0))
        tech_support = str(raw.get("TechSupport", ""))
        online_sec = str(raw.get("OnlineSecurity", ""))
        pay_method = str(raw.get("PaymentMethod", ""))
        internet_svc = str(raw.get("InternetService", ""))

        if contract == "Month-to-month":
            factors.append({
                "factor": "Contract Type",
                "impact": "High Risk Driver",
                "detail": "Customer is on a Month-to-month plan with no long-term commitment."
            })
        elif contract in ["One year", "Two year"]:
            factors.append({
                "factor": "Contract Type",
                "impact": "Retention Anchor",
                "detail": f"Signed under a {contract} contract which dramatically lowers churn odds."
            })

        if tenure <= 6:
            factors.append({
                "factor": "Short Tenure",
                "impact": "High Risk Driver",
                "detail": f"Customer has only been active for {tenure} month(s). Early onboarding stage has highest churn rate."
            })
        elif tenure >= 24:
            factors.append({
                "factor": "Long-term Tenure",
                "impact": "Loyalty Indicator",
                "detail": f"Customer has maintained tenure for {tenure} months, representing an established account."
            })

        if internet_svc == "Fiber optic" and tech_support == "No":
            factors.append({
                "factor": "Unsupported High-Speed Service",
                "impact": "Friction Point",
                "detail": "Customer subscribes to Fiber optic internet but lacks Tech Support or Online Security add-ons."
            })

        if monthly > 80:
            factors.append({
                "factor": "Above Average Monthly Cost",
                "impact": "Price Sensitivity",
                "detail": f"Monthly billing of ${monthly:.2f} puts customer in top tier price bracket."
            })

        if pay_method == "Electronic check":
            factors.append({
                "factor": "Payment Method",
                "impact": "Behavioral Risk",
                "detail": "Historical data shows manual Electronic check payers churn 2.5x more often than automated payers."
            })

        return factors

    def _generate_retention_strategies(self, raw: Dict[str, Any], factors: List[Dict[str, str]]) -> List[Dict[str, str]]:
        strategies = []
        contract = str(raw.get("Contract", ""))
        tech_support = str(raw.get("TechSupport", ""))
        pay_method = str(raw.get("PaymentMethod", ""))
        monthly = float(raw.get("MonthlyCharges", 0.0))

        if contract == "Month-to-month":
            strategies.append({
                "title": "Contract Transition Incentive",
                "action": "Offer a 15% promotional discount on a 1-year or 2-year contract upgrade.",
                "priority": "High Priority"
            })

        if tech_support == "No":
            strategies.append({
                "title": "Complimentary Tech Support Trial",
                "action": "Bundle free 3-month Premium Tech Support & Online Security to increase stickiness.",
                "priority": "High Priority"
            })

        if pay_method == "Electronic check":
            strategies.append({
                "title": "Automated Billing Incentive",
                "action": "Provide a one-time $10 bill credit for switching to Credit Card or Bank Auto-Pay.",
                "priority": "Medium Priority"
            })

        if monthly > 80:
            strategies.append({
                "title": "Plan Optimization Review",
                "action": "Proactively reach out with a customer loyalty consultation to tailor services to budget.",
                "priority": "Medium Priority"
            })

        if not strategies:
            strategies.append({
                "title": "Loyalty Appreciation",
                "action": "Enroll customer in VIP loyalty perks program to reinforce brand satisfaction.",
                "priority": "Standard"
            })

        return strategies
