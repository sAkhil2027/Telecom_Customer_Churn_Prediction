from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CustomerData(BaseModel):
    gender: str = Field(..., example="Female")
    SeniorCitizen: str = Field(..., example="No")
    Partner: str = Field(..., example="No")
    Dependents: str = Field(..., example="No")
    tenure: int = Field(..., ge=1, le=100, example=3)
    PhoneService: str = Field(..., example="Yes")
    MultipleLines: str = Field(..., example="No")
    InternetService: str = Field(..., example="Fiber optic")
    OnlineSecurity: str = Field(..., example="No")
    OnlineBackup: str = Field(..., example="No")
    DeviceProtection: str = Field(..., example="No")
    TechSupport: str = Field(..., example="No")
    StreamingTV: str = Field(..., example="Yes")
    StreamingMovies: str = Field(..., example="No")
    Contract: str = Field(..., example="Month-to-month")
    PaperlessBilling: str = Field(..., example="Yes")
    PaymentMethod: str = Field(..., example="Electronic check")
    MonthlyCharges: float = Field(..., ge=0, example=85.5)
    TotalCharges: Optional[float] = Field(None, example=256.5)

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
