import os
import io
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,JSONResponse

import sys

# Ensure root directory is on python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from backend.schemas import CustomerData, PredictionResult, BatchPredictionResponse, BatchItemResult
    from backend.predictor import ChurnPredictor
except (ImportError, ModuleNotFoundError):
    from schemas import CustomerData, PredictionResult, BatchPredictionResponse, BatchItemResult
    from predictor import ChurnPredictor

app = FastAPI(
    title="Telecom Customer Churn Prediction API",
    description="Production Machine Learning API for predicting telecom customer churn, risk analysis, and retention recommendations.",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
try:
    predictor = ChurnPredictor()
except Exception as e:
    print(f"Warning: Predictor failed to load initially: {e}")
    predictor = None

# Paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(base_dir, "frontend")

@app.get("/api/health")
def health_check():
    if predictor is None:
        return {"status": "unhealthy", "error": "Model artifacts not loaded"}
    return {
        "status": "healthy",
        "model_type": "GradientBoostingClassifier (Tuned)",
        "metrics": predictor.metrics,
        "features_count": len(predictor.feature_order)
    }

@app.post("/api/predict", response_model=PredictionResult)
def predict_churn(customer: CustomerData):
    if predictor is None:
        raise HTTPException(status_code=500, detail="Prediction model is not initialized.")
    try:
        payload = customer.model_dump()
        result = predictor.predict(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")

