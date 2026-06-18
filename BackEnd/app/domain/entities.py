
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class UserEntity(BaseModel):
    employee_id: str
    email: str
    password: str
    role: str

class AneurysmPrediction(BaseModel):
    present: float


class LocationPredictions(BaseModel):
    LeftInfraclinoidInternalCarotidArtery: float
    RightInfraclinoidInternalCarotidArtery: float
    LeftSupraclinoidInternalCarotidArtery: float
    RightSupraclinoidInternalCarotidArtery: float
    LeftMiddleCerebralArtery: float
    RightMiddleCerebralArtery: float
    AnteriorCommunicatingArtery: float
    LeftAnteriorCerebralArtery: float
    RightAnteriorCerebralArtery: float
    LeftPosteriorCommunicatingArtery: float
    RightPosteriorCommunicatingArtery: float
    BasilarTip: float
    OtherPosteriorCirculation: float


class AneurysmAnalysisResult(BaseModel):
    overall: AneurysmPrediction
    locations: LocationPredictions

class ScanEntity(BaseModel):
    id: str
    scan_date: datetime
    status: str 
    results: Optional[AneurysmAnalysisResult] = None

class PatientEntity(BaseModel):
    id: str
    patient_name: str
    image_date: datetime
    scans: List[ScanEntity] = Field(default_factory=list)

    def add_scan(self, scan: ScanEntity) -> None:
        """Domain Rule: Ensure duplicate scan IDs aren't allowed"""
        if scan.id in {s.id for s in self.scans}:
            raise ValueError("Scan ID already exists for this patient")
        self.scans.append(scan)