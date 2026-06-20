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
    name: str
    image_date: datetime
    analyzed: bool
    timestamp: Optional[datetime] = None
    urgency: Optional[str] = None