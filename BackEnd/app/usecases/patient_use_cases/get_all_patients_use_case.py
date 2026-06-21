from app.domain.entities import PatientEntity
from app.domain.repositories import PatientRepository, SettingsRepository
from typing import List


class GetAllPatientsUseCase:
    def __init__(self, patient_repo: PatientRepository, settings_repo: SettingsRepository):
        self.patient_repo = patient_repo
        self.settings_repo = settings_repo  # Assuming you have a way to get settings

    async def execute(self) -> List[PatientEntity] | None:
        patients = await self.patient_repo.get_all_patients()
        return patients
    
