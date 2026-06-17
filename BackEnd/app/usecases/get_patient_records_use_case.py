from app.domain.repositories import PatientRepository
from app.schemas.patient_schema import PatientRecordResponse
from typing import List

class GetPatientRecordsUseCase:
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def execute(self) -> List[PatientRecordResponse] | None:
        patients = await self.patient_repo.get_all_patients()
        if not patients or patients is None:
            return  None
        return [PatientRecordResponse.model_validate(patient) for patient in patients]
    
