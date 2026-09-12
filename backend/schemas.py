from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CustomerData(BaseModel):
    gender: str = Field(..., description="Gender ('Male' or 'Female')")
    SeniorCitizen: str = Field(..., description="Senior Citizen ('Yes' or 'No')")
    Partner: str = Field(..., description="Partner ('Yes' or 'No')")
    Dependents: str = Field(..., description="Dependents ('Yes' or 'No')")
    tenure: int = Field(..., ge=1, le=100, description="Tenure in months (1-100)")
    PhoneService: str = Field(..., description="Phone Service ('Yes' or 'No')")
    MultipleLines: str = Field(..., description="Multiple Lines ('No phone service', 'No', 'Yes')")
    InternetService: str = Field(..., description="Internet Service ('DSL', 'Fiber optic', 'No')")
    OnlineSecurity: str = Field(..., description="Online Security ('Yes', 'No', 'No internet service')")
    OnlineBackup: str = Field(..., description="Online Backup ('Yes', 'No', 'No internet service')")
    DeviceProtection: str = Field(..., description="Device Protection ('Yes', 'No', 'No internet service')")
    TechSupport: str = Field(..., description="Tech Support ('Yes', 'No', 'No internet service')")
    StreamingTV: str = Field(..., description="Streaming TV ('Yes', 'No', 'No internet service')")
    StreamingMovies: str = Field(..., description="Streaming Movies ('Yes', 'No', 'No internet service')")
    Contract: str = Field(..., description="Contract ('Month-to-month', 'One year', 'Two year')")
    PaperlessBilling: str = Field(..., description="Paperless Billing ('Yes' or 'No')")
    PaymentMethod: str = Field(..., description="Payment Method ('Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)')")
    MonthlyCharges: float = Field(..., ge=0, description="Monthly Charges (USD)")
    TotalCharges: Optional[float] = Field(None, description="Total Charges (USD, auto-calculated if omitted)")

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "Female",
                "SeniorCitizen": "No",
                "Partner": "No",
                "Dependents": "No",
                "tenure": 3,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "Yes",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 85.5,
                "TotalCharges": 256.5
            }
        }

class RiskFactor(BaseModel):
    factor: str
    impact: str
    detail: str

class RetentionStrategy(BaseModel):
    title: str
    action: str
    priority: str

class PredictionResult(BaseModel):
    churn_prediction: str
    churn_code: int
    churn_probability: float
    retention_probability: float
    risk_level: str
    risk_color: str
    risk_factors: List[RiskFactor]
    retention_strategies: List[RetentionStrategy]
    metrics: Dict[str, Any]

class BatchItemResult(BaseModel):
    row_id: int
    churn_prediction: str
    churn_probability: float
    risk_level: str

class BatchPredictionResponse(BaseModel):
    total_processed: int
    high_risk_count: int
    churn_rate_predicted: float
    predictions: List[BatchItemResult]
