import os
import uvicorn
from backend.export_model import train_and_export

def check_artifacts():
    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "artifacts")
    model_file = os.path.join(artifacts_dir, "churn_model.pkl")
    if not os.path.exists(model_file):
        print("Model artifacts not detected. Training and exporting model...")
        train_and_export()
    else:
        print("[OK] Found trained model artifacts in backend/artifacts/")

def main():
    check_artifacts()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    print("\n" + "=" * 60)
    print(" >>> TELECOM CUSTOMER CHURN PREDICTION APPLICATION")
    print(f" * Server running on: http://{host}:{port}")
    print(f" * API Documentation: http://{host}:{port}/docs")
    print("=" * 60 + "\n")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
