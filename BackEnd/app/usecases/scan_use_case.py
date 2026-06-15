from app.services.data_layer import NoSQLDataLayer
from app.services.ai_service import AIService
from app.services.data_layer import get_data_layer
from app.services.ai_service import get_ai_service

class ScanAnalysisUseCase:
    def __init__(self, data_layer: NoSQLDataLayer, ai_service: AIService):
        self.data_layer = data_layer
        self.ai_service = ai_service
    async def execute(self, scan_id: str) -> dict:
        binary_data = await self.data_layer.get_scan_binary_data(scan_id)
        if not binary_data:
            raise ValueError("Scan record not found in NoSQL layer")
            
        analysis_results = await self.ai_service.request_scan_analysis(
            scan_id=scan_id, 
            binary_data=binary_data
        )
        
        await self.data_layer.update_scan_results(scan_id, results=analysis_results)
        return analysis_results

def get_scan_analysis_use_case() -> ScanAnalysisUseCase:
    return ScanAnalysisUseCase(
        data_layer=get_data_layer(), 
        ai_service=get_ai_service()
    )