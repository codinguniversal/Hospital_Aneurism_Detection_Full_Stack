
from datetime import datetime, date
from typing import  List, Optional
from app.config import  Settings

from pydantic import BaseModel, Field

from enum import Enum
class ScanStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
class ScanUrgency(str, Enum):
    UNKOWN = "Unkown"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class UserEntity(BaseModel):
    employee_id: str
    email: str
    password: str
    role: str

class OverAllAneurysmPrediction(BaseModel):
    probability: float


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
    overall: Optional[OverAllAneurysmPrediction] = None
    locations: Optional[LocationPredictions] = None

class ScanEntity(BaseModel):
    id: str
    scan_date: datetime
    status: ScanStatus  # Pending | Processing | Completed | Failed
    img_file_path: str
    scan_analysis_date: Optional[datetime] = None
    results: Optional[AneurysmAnalysisResult] = None
    
    @property
    def urgency(self)-> str:
        """
        Domain Rule calculate the urgency based on
        the AI Overall Results and configurable thresholds
        """
        if (
            not self.results 
            or self.results.overall is None 
            or getattr(self.results.overall, "probability", None) is None
        ):
            return ScanUrgency.UNKOWN.value
        
        probability = self.results.overall.probability
        if probability >= Settings.aneurysm_high_risk_threshold:
            return  ScanUrgency.HIGH.value
        if probability >= Settings.aneurysm_medium_risk_threshold:
            return  ScanUrgency.MEDIUM.value
        return  ScanUrgency.LOW.value

class PatientEntity(BaseModel):
    id: str
    patient_name: str
    birth_date: date
    assigned_doc: str
    medical_history: List[str] = Field(default_factory=list)
    scans: List[ScanEntity] = Field(default_factory=list)

    def add_scan(self, scan: ScanEntity) -> None:
        """Domain Rule: Ensure duplicate scan IDs aren't allowed"""
        if scan.id in {s.id for s in self.scans}:
            raise ValueError("Scan ID already exists for this patient")
        self.scans.append(scan)