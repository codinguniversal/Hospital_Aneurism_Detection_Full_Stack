from app.domain.repositories import PatientRepository
from app.domain.entities import PatientEntity
from typing import Optional

class GetPatientResultsUseCase:
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo
    async def execute( self, patient_id: str) -> Optional[PatientEntity]:
        
        if not patient_id:
            return None
        patient = await self.patient_repo.get_patient_by_id(patient_id)
        if not patient:
            return None
        return patient