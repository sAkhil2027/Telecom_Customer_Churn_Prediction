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
