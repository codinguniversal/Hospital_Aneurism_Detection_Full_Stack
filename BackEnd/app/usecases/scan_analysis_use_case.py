from fastapi import Depends

from app.repositories.mock_patient_repository import MockPatientRepository
from app.services.mock_data_layer import NoSQLDataLayer
from app.services.ai_service import AIService
from app.domain.repositories import PatientRepository
from app.services.mock_data_layer import get_data_layer
from app.services.ai_service import get_ai_service

class ScanAnalysisUseCase:
    def __init__(self, patient_repo: PatientRepository, ai_service: AIService):
        self.patient_repo = patient_repo
        self.ai_service = ai_service

    async def execute(self, scan_id: str) -> dict:
        binary_data = await self.patient_repo.get_scan_binary_data(scan_id)
        if not binary_data:
            raise ValueError(f"Scan record with id {scan_id} not found in DB")
            
        analysis_results = await self.ai_service.request_scan_analysis(
            scan_id=scan_id, 
            binary_data=binary_data
        )
        
        await self.patient_repo.update_scan_results(scan_id, results=analysis_results)
        return analysis_results

