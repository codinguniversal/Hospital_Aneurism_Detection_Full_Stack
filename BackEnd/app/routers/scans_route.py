from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from BackEnd.app.schemas.patient_schema import ScanAnalysisRequest
from app.services.ai_service import  AIServiceError 
from BackEnd.app.usecases.scan_analysis_use_case import ScanAnalysisUseCase
from app.dependencies import get_scan_analysis_use_case

router = APIRouter(
    prefix="/api/scans",
    tags = ["AI Scanning"]
)

@router.post("/{scan_id}/analyze", status_code= status.HTTP_200_OK)
async def run_manual_analysis(
    scan_id: str,
    analysis_request : ScanAnalysisRequest,
    use_case: ScanAnalysisUseCase = Depends(get_scan_analysis_use_case)
):
    """
    Endpoint triggered when Run Analysis button in front end table is pressed
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
    except AIServiceError as exc:
        raise HTTPException(
            status_code = exc.status_code,
            detail = str(exc)
        )