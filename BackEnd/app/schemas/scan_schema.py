from datetime import datetime
from datetime import datetime
from typing import Any 

from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.domain.entities import AneurysmAnalysisResultEntity



class ScanCreateSchema(BaseModel):
    id: str
    img_file_path: str  # Frontend tells API where the raw zip/DICOM file was saved on E:



class ScanAnalysisRequest(BaseModel):
    patient_name: str
    patient_id: Optional[str] = None
    scan_id: str

class ScanAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes= True)

    status: str
    patient_name: str
    scan_id: str
    analysis_timestamp: datetime
    result: AneurysmAnalysisResultEntity