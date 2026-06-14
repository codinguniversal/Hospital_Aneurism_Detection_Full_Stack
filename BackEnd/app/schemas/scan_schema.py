from pydantic import BaseModel

class ScanAnalysisRequest(BaseModel):
    patient_name: str
    patient_id: str
    scan_id: str