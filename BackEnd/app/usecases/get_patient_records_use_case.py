from app.domain.repositories import PatientRepository
from app.domain.entities import PatientEntity
from app.schemas.patient_schema import PatientRecordResponse
from typing import List

class GetPatientRecordsUseCase:
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def execute(self) -> List[PatientEntity] | None:
        patients = await self.patient_repo.get_all_patients()
        return patients or []
    
