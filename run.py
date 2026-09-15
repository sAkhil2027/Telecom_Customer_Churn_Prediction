import os
import uvicorn
from backend.export_model import train_and_export

def check_artifacts():
    model_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "artifacts", "churn_model.pkl")
    if not os.path.exists(model_file):
        print("Model artifacts not detected. Training and exporting model...")
        train_and_export()
    else:
        print("[OK] Found trained model artifacts in backend/artifacts/")

def main():
    check_artifacts()
    print("\n" + "=" * 60)
    print(" >>> TELECOM CUSTOMER CHURN PREDICTION APPLICATION")
    print(" * Web Dashboard:     http://127.0.0.1:8000")
    print(" * API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
