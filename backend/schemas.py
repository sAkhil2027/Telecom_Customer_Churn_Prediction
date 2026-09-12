from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CustomerData(BaseModel):
    gender: str = Field(..., description="Gender ('Male' or 'Female')")
    SeniorCitizen: str = Field(..., description="Senior Citizen ('Yes' or 'No')")
    Partner: str = Field(..., description="Partner ('Yes' or 'No')")
    Dependents: str = Field(..., description="Dependents ('Yes' or 'No')")
