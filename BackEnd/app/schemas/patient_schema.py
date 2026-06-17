from pydantic import BaseModel, Field
from typing import List

from BackEnd.app.schemas.scan_schema import ScanResponseSchema


class PatientCreateSchema(BaseModel):
    id: str
    patient_name: str
    birth_date: str
    assigned_doc: str
    medical_history: List[str] = Field(default_factory=list)

class PatientResponseSchema(BaseModel):
    id: str
    patient_name: str
    birth_date: str
    assigned_doc: str
    medical_history: List[str]
    scans: List[ScanResponseSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True