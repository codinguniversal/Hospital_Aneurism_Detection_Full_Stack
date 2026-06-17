from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

class ScanCreateSchema(BaseModel):
    id: str
    img_file_path: str  # Frontend tells API where the raw zip/DICOM file was saved on E:

class ScanResponseSchema(BaseModel):
    id: str
    scan_date: datetime
    status: str
    img_file_path: str
    results: Optional[Dict] = None

    class Config:
        from_attributes = True