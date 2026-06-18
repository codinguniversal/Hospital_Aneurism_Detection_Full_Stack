
from datetime import datetime
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
    scan_date: datetime
    status: str 
    binary_data: bytes
    results: Optional[Dict] = None

class PatientEntity(BaseModel):
    id: str
    patient_name: str
    image_date: datetime
    scans: List[ScanEntity] = Field(default_factory=list)

    def add_scan(self, scan: ScanEntity):
        """Domain Rule: Ensure duplicate scan IDs aren't allowed"""
        if any(s.id == scan.id for s in self.scans):
            raise ValueError("Scan ID already exists for this patient")
        self.scans.append(scan)