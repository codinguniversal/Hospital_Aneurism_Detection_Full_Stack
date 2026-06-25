from datetime import datetime, date
from enum import Enum
from typing import Any, List, Optional, Self

from pydantic import BaseModel, Field, model_validator

MAXNUMOFEXPLAINEDSLICES = 5

class ScanStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanUrgency(str, Enum):
    UNKNOWN = "Unknown"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


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

class TopSliceEntity(BaseModel):
    slice_index: int
    importance: float
    overlay_image_ref: str

class ExplainabilityEntity(BaseModel):
    id:str
    method:str ="Grad-CAM"
    target_label: str
    top_slices: List[TopSliceEntity] = Field(min_length= 1, max_length=MAXNUMOFEXPLAINEDSLICES)
    model_metadata: Optional[Any] = None


class AneurysmAnalysisResultEntity(BaseModel):
    overall: Optional[OverAllAneurysmPredictionEntity] = None
    locations: Optional[LocationPredictionsEntity] = None
    explainability: Optional[List[ExplainabilityEntity]] = Field(default_factory= list)


class ScanEntity(BaseModel):
    id: str
    scan_date: datetime
    status: ScanStatus
    img_file_path: str
    scan_analysis_date: Optional[datetime] = None
    results: Optional[AneurysmAnalysisResultEntity] = None

    def urgency(self, high_threshold: float, mid_threshold: float) -> str:
        if (
            not self.results
            or self.results.overall is None
            or getattr(self.results.overall, "probability", None) is None
        ):
            return ScanUrgency.UNKNOWN.value

        probability = self.results.overall.probability
        if probability >= high_threshold:
            return ScanUrgency.HIGH.value
        if probability >= mid_threshold:
            return ScanUrgency.MEDIUM.value
        return ScanUrgency.LOW.value


class PatientEntity(BaseModel):
    id: str
    patient_name: str
    birth_date: date
    assigned_doc: str
    medical_history: List[str] = Field(default_factory=list)
    scans: List[ScanEntity] = Field(default_factory=list)

    def add_scan(self, scan: ScanEntity) -> None:
        if scan.id in {s.id for s in self.scans}:
            raise ValueError("Scan ID already exists for this patient")
        self.scans.append(scan)
