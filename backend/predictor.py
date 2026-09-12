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

