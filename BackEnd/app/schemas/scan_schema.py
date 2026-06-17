from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

class ScanAnalysisRequest(BaseModel):
    patient_name: str
    patient_id: str
    scan_id: str

class ScanAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes= True)

    status: str
    patient_name: str
    scan_id: str
    analysis_timestamp: datetime
    result: Any