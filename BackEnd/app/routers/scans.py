import httpx
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.schemas.scan_schema import ScanAnalysisRequest
from app.services.data_layer import get_data_layer, NoSQLDataLayer
from app.services.ai_service import AIService , get_ai_service
from BackEnd.app.services.usecases.scan_use_case import ScanAnalysisUseCase, get_manual_scan_analysis_use_case


router = APIRouter(
    prefix="/scans",
    tags = ["AI Scanning"]
)


@router.post("/analyze-manual", status_code= status.HTTP_200_OK)
async def run_manual_analysis(
    analysis_request : ScanAnalysisRequest,
    use_case: ScanAnalysisUseCase = Depends(get_manual_scan_analysis_use_case)
):
    """
    endpoint triggered when Run Analysis button in front end table is pressed
    calls backend for the scans, then we call the ai service via network call  for results
    """
    try:
        analysis_results = await use_case.execute(analysis_request.scan_id)

        return {
            "status": "completed",
            "patient_name": analysis_request.patient_name,
            "scan_id": analysis_request.scan_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "result": analysis_results
        }
    except ValueError as exc:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= str(exc)
        )