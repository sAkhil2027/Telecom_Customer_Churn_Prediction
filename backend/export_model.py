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

    # Features and target split
    feature_order = [c for c in df_encoded.columns if c != target_col]
    X = df_encoded[feature_order]
    y = df_encoded[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=4, stratify=y
    )

    # Fit scaler on numeric columns
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test_scaled[num_cols] = scaler.transform(X_test[num_cols])

    print("Training tuned GradientBoostingClassifier...")
    # Best model hyperparameters discovered in notebook
    model = GradientBoostingClassifier(max_depth=2, n_estimators=250, learning_rate=0.08, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_prob))

    print(f"Model Performance -> Accuracy: {acc*100:.2f}%, ROC-AUC: {roc_auc*100:.2f}%")

    # Extract feature importances
    feature_importances = dict(zip(feature_order, [float(v) for v in model.feature_importances_]))
    sorted_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

    # Save artifacts
    model_path = os.path.join(artifacts_dir, "churn_model.pkl")
    scaler_path = os.path.join(artifacts_dir, "scaler.pkl")
    meta_path = os.path.join(artifacts_dir, "meta.json")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "feature_order": feature_order,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "cat_mappings": cat_mappings,
        "target_mapping": target_mapping,
        "metrics": {
            "accuracy": round(acc * 100, 2),
            "roc_auc": round(roc_auc * 100, 2)
        },
        "feature_importances": sorted_importances
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Successfully exported artifacts to {artifacts_dir}:")
    print(f" - {model_path}")
    print(f" - {scaler_path}")
    print(f" - {meta_path}")

if __name__ == "__main__":
    train_and_export()
