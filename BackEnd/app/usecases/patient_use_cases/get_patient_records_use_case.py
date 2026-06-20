from datetime import datetime

from pydantic import BaseModel

from app.domain.repositories import PatientRepository, SettingsRepository
from typing import List

class PatientRecordSnapshot(BaseModel):
    """This class represents the result of a patient record retrieval operation.
    It is not an entity nor a DTO, but rather a simple data structure to hold the results of the use case execution.
    Do not confuse with PatientRecordResponse, which is a DTO used for API responses.
    """
    id: str
    name: str
    image_date: datetime
    analyzed: bool
    urgency: str

class GetPatientRecordsUseCase:
    def __init__(self, patient_repo: PatientRepository, settings_repo: SettingsRepository):
        self.patient_repo = patient_repo
        self.settings_repo = settings_repo  # Assuming you have a way to get settings

    async def execute(self) -> List[PatientRecordSnapshot] | None:
        patients = await self.patient_repo.get_all_patients()
        settings = await self.settings_repo.get_settings()
        high_threshold = settings.aneurysm_high_risk_threshold
        mid_threshold = settings.aneurysm_medium_risk_threshold
        results = []
        for patient in patients:
            if not patient.scans:
                continue  # Skip patients without scans
            latest_scan = patient.scans[0]  # Assuming the first scan is the latest; adjust if necessary
            urgency = latest_scan.urgency(high_threshold=high_threshold, mid_threshold=mid_threshold)
            results.append(
                PatientRecordSnapshot(                
                    id= patient.id,
                    name=patient.patient_name,
                    image_date=latest_scan.scan_date,
                    analyzed=latest_scan.status == "Completed",
                    urgency=urgency
                )
            )
                
        return results
    
