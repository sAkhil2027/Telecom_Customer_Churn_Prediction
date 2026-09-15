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
