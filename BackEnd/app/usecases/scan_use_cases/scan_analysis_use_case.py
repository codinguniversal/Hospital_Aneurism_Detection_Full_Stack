from app.domain.entities import AneurysmAnalysisResultEntity
from app.services.ai_service import AIService
from app.domain.repositories import PatientRepository


class ScanAnalysisUseCase:
    def __init__(self, patient_repo: PatientRepository, ai_service: AIService):
        self.patient_repo = patient_repo
        self.ai_service = ai_service

    async def execute(self, scan_id: str) -> AneurysmAnalysisResultEntity:
        binary_data = await self.patient_repo.get_scan_file(scan_id)
        if not binary_data:
            raise ValueError(f"Scan record with id {scan_id} not found in DB")
            
        analysis_results = await self.ai_service.request_scan_analysis(
            scan_id=scan_id, 
            binary_data=binary_data
        )
        
        await self.patient_repo.update_scan_results(
            scan_id=scan_id,
            ai_results=analysis_results
        )
        return analysis_results