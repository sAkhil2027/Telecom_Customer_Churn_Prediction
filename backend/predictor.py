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
