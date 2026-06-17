from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel,ConfigDict





class PatientRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes= True)

    id: str
    name: str
    image_date: datetime
    analyzed: bool
    timestamp: Optional[datetime] = None
    urgency: Optional[str] = None
class PatientRecordsListResponse(BaseModel):
    model_config = ConfigDict(from_attributes= True)
    records: List[PatientRecordResponse]
