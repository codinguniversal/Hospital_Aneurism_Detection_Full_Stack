import httpx
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.schemas.scan_schema import ScanAnalysisRequest
from app.services.data_layer import get_data_layer, NoSQLDataLayer
from app.services.ai_service import AIService , get_ai_service


router = APIRouter(
    prefix="/scans",
    tags = ["AI Scanning"]
)


@router.post("/analyze-manual", status_code= status.HTTP_200_OK)
async def run_manual_analysis(
    analysis_request : ScanAnalysisRequest,
    data_layer: NoSQLDataLayer = Depends(get_data_layer),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    endpoint triggered when Run Analysis button in front end table is pressed
    calls backend for the scans, then we call the ai service via network call  for results
    """
    binary_data = await data_layer.get_scan_binary_data(analysis_request.scan_id)
    if not binary_data:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="Scan record not found in NoSQL layer"
        )
    analysis_results = await ai_service.request_scan_analysis(
        scan_id = analysis_request.scan_id,
        binary_data= binary_data
    )
    await data_layer.update_scan_results(analysis_request.scan_id, results=analysis_results)

    return {
        "status": "completed",
        "patient_name": analysis_request.patient_name,
        "scan_id": analysis_request.scan_id,
        "analysis_timestamp": datetime.now().isoformat(),
        "result": analysis_results
    }