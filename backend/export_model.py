import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

def train_and_export():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    # Locate dataset
    data_paths = [
        os.path.join(base_dir, "..", "data.csv"),
        os.path.join(base_dir, "data.csv"),
        os.path.join(base_dir, "..", "Scripts", "data.csv")
    ]
    data_path = None
    for p in data_paths:
        if os.path.exists(p):
            data_path = p
            break

    if not data_path:
        raise FileNotFoundError("Could not find data.csv")

    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)

    # Data Preprocessing as done in the notebook
    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df[df["tenure"] != 0].copy()
    df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].mean())
    df["SeniorCitizen"] = df["SeniorCitizen"].replace({0: "No", 1: "Yes"})

    target_col = "Churn"
    num_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    cat_cols = [c for c in df.columns if c not in num_cols and c != target_col]

    # Save mapping for categorical variables
    encoders = {}
    cat_mappings = {}
    df_encoded = df.copy()

    for c in cat_cols:
        le = LabelEncoder()
        df_encoded[c] = le.fit_transform(df[c].astype(str))
        encoders[c] = le
        cat_mappings[c] = {str(cls_val): int(code) for code, cls_val in enumerate(le.classes_)}

    # Target variable encoding (No: 0, Yes: 1)
    target_le = LabelEncoder()
    df_encoded[target_col] = target_le.fit_transform(df[target_col])
    target_mapping = {str(cls_val): int(code) for code, cls_val in enumerate(target_le.classes_)}

