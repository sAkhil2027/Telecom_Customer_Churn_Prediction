import os
import io
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.schemas import CustomerData, PredictionResult, BatchPredictionResponse, BatchItemResult
from backend.predictor import ChurnPredictor

app = FastAPI(
    title="Telecom Customer Churn Prediction API",
    description="Production Machine Learning API for predicting telecom customer churn, risk analysis, and retention recommendations.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    predictor = ChurnPredictor()
except Exception as e:
    print(f"Warning: Predictor failed to load initially: {e}")
    predictor = None

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
        return predictor.predict(customer.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")
