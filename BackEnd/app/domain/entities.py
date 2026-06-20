
from datetime import datetime, date
from typing import  List, Optional, Self

from pydantic import BaseModel, Field, HttpUrl, model_validator

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

class SettingsEntity(BaseModel):
    # AI and Analysis
    ai_api_url: HttpUrl
    ai_timeout_limit: int = Field(gt=0, description="AI timeout limit must be a positive integer.")
    # automatic scan scheduling
    automatic_scan_start_hour:  int = Field(ge=0, le=23, description="Start hour must be between 0 and 23.")
    automatic_scan_end_hour: int = Field(ge=0, le=23, description="End hour must be between 0 and 23.")
    automatic_scan_interval: int = Field(gt=0, description="Scan interval must be a positive integer.")
    # urgency definition
    aneurysm_high_risk_threshold: float = Field(gt=0, lt=1, description="High risk threshold must be between 0 and 1.")
    aneurysm_medium_risk_threshold: float = Field(gt=0, lt=1, description="Medium risk threshold must be between 0 and 1.")
    @model_validator(mode="after")
    def validate_business_invariants(self) -> Self:
        """ Ensures cross-field business rules are met (e.g., high risk threshold > medium risk threshold)"""
        if self.aneurysm_high_risk_threshold <= self.aneurysm_medium_risk_threshold:
            raise ValueError("High risk threshold must be greater than medium risk threshold.")
        if self.automatic_scan_start_hour >= self.automatic_scan_end_hour:
            raise ValueError("Start hour must be less than end hour.")
        return self

class UserEntity(BaseModel):
    employee_id: str
    email: str
    password: str
    role: str

class OverAllAneurysmPredictionEntity(BaseModel):
    probability: float


class LocationPredictionsEntity(BaseModel):
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



class AneurysmAnalysisResultEntity(BaseModel):
    overall: Optional[OverAllAneurysmPredictionEntity] = None
    locations: Optional[LocationPredictionsEntity] = None

class ScanEntity(BaseModel):
    id: str
    scan_date: datetime
    status: ScanStatus  # Pending | Processing | Completed | Failed
    img_file_path: str
    scan_analysis_date: Optional[datetime] = None
    results: Optional[AneurysmAnalysisResultEntity] = None
    
    def urgency(self, high_threshold: float, mid_threshold: float)-> str:
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
        if probability >= high_threshold:
            return  ScanUrgency.HIGH.value
        if probability >= mid_threshold:
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