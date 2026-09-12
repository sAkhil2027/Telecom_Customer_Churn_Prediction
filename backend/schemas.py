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
