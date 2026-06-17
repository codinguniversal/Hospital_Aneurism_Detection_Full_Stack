from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScanAnalysisRequest(BaseModel):
    patient_name: str
    patient_id: str
    scan_id: str

class PatientRecordResponse(BaseModel):
    id: str
    name: str
    imageDate: datetime
    analyzed: bool
    timestamp: Optional[datetime] = None
    urgency: Optional[str] = None

    class config:
        from_attributes= True