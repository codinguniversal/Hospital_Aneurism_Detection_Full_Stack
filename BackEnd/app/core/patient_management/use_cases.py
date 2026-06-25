from typing import List, Optional

from app.core.patient_management.entities import AneurysmAnalysisResultEntity, PatientEntity
from app.core.patient_management.repositories import PatientRepository
from app.core.patient_management.services import ScanAnalysisService
from app.modules.system_settings.repositories import SettingsRepository


class GetAllPatientsUseCase:
    def __init__(self, patient_repo: PatientRepository, settings_repo: SettingsRepository):
        self.patient_repo = patient_repo
        self.settings_repo = settings_repo

    async def execute(self) -> List[PatientEntity] | None:
        patients = await self.patient_repo.get_all_patients()
        return patients


class GetPatientResultsUseCase:
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def execute(self, patient_id: str) -> Optional[PatientEntity]:
        if not patient_id:
            return None
        patient = await self.patient_repo.get_patient_by_id(patient_id)
        if not patient:
            return None
        return patient
 
class ScanAnalysisUseCase:
    def __init__(self, patient_repo: PatientRepository, ai_service: ScanAnalysisService):
        self.patient_repo = patient_repo
        self.ai_service = ai_service

    async def execute(self, scan_id: str) -> AneurysmAnalysisResultEntity:
        binary_data = await self.patient_repo.get_scan_file(scan_id)
        if not binary_data:
            raise ValueError(f"Scan record with id {scan_id} not found in DB")

        analysis_results = await self.ai_service.analyze_scan(
            scan_id= scan_id,
            binary_data= binary_data,
            explain= False
        )

        await self.patient_repo.update_scan_results(
            scan_id=scan_id,
            ai_results=analysis_results,
        )
        return analysis_results
