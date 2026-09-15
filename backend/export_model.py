import os
import json
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

def load_and_preprocess_data(base_dir):
    data_path = os.path.join(base_dir, "..", "data.csv")
    if not os.path.exists(data_path):
        data_path = os.path.join(base_dir, "data.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"data.csv not found relative to {base_dir}")

    df = pd.read_csv(data_path)
    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df[df["tenure"] != 0].copy()
    df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].mean())
    df["SeniorCitizen"] = df["SeniorCitizen"].replace({0: "No", 1: "Yes"})
    return df

def encode_features(df):
    target_col = "Churn"
    num_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    cat_cols = [c for c in df.columns if c not in num_cols and c != target_col]

    cat_mappings = {}
    df_encoded = df.copy()

    for c in cat_cols:
        le = LabelEncoder()
        df_encoded[c] = le.fit_transform(df[c].astype(str))
        cat_mappings[c] = {str(k): int(v) for v, k in enumerate(le.classes_)}

    target_le = LabelEncoder()
    df_encoded[target_col] = target_le.fit_transform(df[target_col])
    target_mapping = {str(k): int(v) for v, k in enumerate(target_le.classes_)}

    feature_order = [c for c in df_encoded.columns if c != target_col]
    return df_encoded, feature_order, num_cols, cat_cols, cat_mappings, target_mapping
