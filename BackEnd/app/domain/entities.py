from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class UserEntity(BaseModel):
    employee_id: str
    email: str
    password: str
    role: str

class ScanEntity(BaseModel):
    id: str
    patient_id: str
    scan_date: str
    status: str
    binary_data: bytes
    results: Optional[Dict] = None

class PatientEntity(BaseModel):
    id: str
    patient_name: str
    scans: List[ScanEntity] = Field(default_factory=list)
