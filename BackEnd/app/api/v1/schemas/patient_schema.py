from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel,ConfigDict,Field

class PatientCreateRequestSchema(BaseModel):
    id: str
    patient_name: str
    birth_date: str
    assigned_doc: str
    medical_history: List[str] = Field(default_factory=list)




class PatientRecordResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes= True)

    id: str
    scan_id: str
    name: str
    assigned_doc: str
    scan_date: datetime
    analyzed: bool
    scan_analysis_date: Optional[datetime] = None
    urgency: Optional[str] = None