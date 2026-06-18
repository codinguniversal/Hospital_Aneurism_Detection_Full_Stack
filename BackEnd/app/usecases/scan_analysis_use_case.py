import os
from app.domain.entities import AneurysmAnalysisResult
from app.services.ai_service import AIService
from app.domain.repositories import PatientRepository


class ScanAnalysisUseCase:
    def __init__(self, patient_repo: PatientRepository, ai_service: AIService):
        self.patient_repo = patient_repo
        self.ai_service = ai_service

    async def execute(self, scan_id: str) -> AneurysmAnalysisResult:
        #Fetch file storage path from MongoDB using our clean refactored method
        file_path = await self.patient_repo.get_scan_file_path(scan_id)
        if not file_path:
            raise ValueError(f"Scan record with id {scan_id} not found in DB")
            
        #Safety check: ensure file path actually exists physically on host machine
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The patient scan file was not found at target path: {file_path}")
            
        # Read raw binary bytes from disk storage
        with open(file_path, "rb") as file_bytes:
            binary_data = file_bytes.read()
    
            #  Stream to AI Engine matching your exact OG positional/keyword signature
            analysis_results = await self.ai_service.request_scan_analysis(
                scan_id=scan_id, 
                binary_data=binary_data
            )
        
        # Persist the Domain Entity data back into MongoDB.
        # MongoDB expects a raw dictionary payload for its update filters, so we convert the entity.
        await self.patient_repo.update_scan_results(scan_id, results=analysis_results.model_dump())
        
        return analysis_results