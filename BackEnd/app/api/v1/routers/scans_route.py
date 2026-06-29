from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from app.api.v1.schemas.scan_schema import ScanAnalysisRequestSchema, ScanAnalysisResponseSchema
from app.core.patient_management.use_cases import ScanAnalysisUseCase
from app.modules.system_settings.use_cases import GetSettingsUseCase
from app.infrastructure.ai.ai_client import AIServiceError
from app.dependencies import build_get_settings_use_case, build_scan_analysis_use_case

router = APIRouter(
    prefix="/api/scans",
    tags=["AI Scanning"]
)

@router.post("/{scan_id}/analyze", response_model=ScanAnalysisResponseSchema, status_code=status.HTTP_200_OK)
async def run_manual_analysis(
    scan_id: str,
    analysis_request: ScanAnalysisRequestSchema,
    target_label: str = "Aneurysm Present", 
    use_case: ScanAnalysisUseCase = Depends(build_scan_analysis_use_case),
    get_settings_use_case: GetSettingsUseCase = Depends(build_get_settings_use_case),
):
    """
    Endpoint triggered when the Run Analysis button in the frontend table is pressed.
    Loads the image filepath, reads the binary data from disk, routes it to the AI microservice,
    and returns the structured payload instantly.
    """
    try:
        # Note: Always pass the clean URL string parameter (scan_id) over the request body object
        # to ensure the path parameter and the body stay completely synchronized.
        analysis_results = await use_case.execute(
                scan_id=scan_id,
                include_heatmap=True,
                target_label = target_label
            )
        settings = await get_settings_use_case.execute()
        urgency = analysis_results.urgency(
            high_threshold=settings.aneurysm_high_risk_threshold,
            mid_threshold=settings.aneurysm_medium_risk_threshold,
        )

        # Map back to your frontend validation response schema
        return ScanAnalysisResponseSchema(
            status="completed",
            patient_name=analysis_request.patient_name,
            scan_id=scan_id,
            analysis_timestamp=datetime.now(),
            urgency=urgency,
            result=analysis_results  # This matches the AneurysmAnalysisResult entity
        )
        
    except ValueError as exc:
        # Triggered if the scan_id isn't found in MongoDB
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    except FileNotFoundError as exc:
        # Triggered if the zip file was deleted or cannot be found on the server volume
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage error: {str(exc)}"
        )
    except AIServiceError as exc:
        # Triggered if the AI container fails or turns up a network connection issue
        raise HTTPException(
            status_code=exc.status_code if hasattr(exc, 'status_code') else 502,
            detail=str(exc)
        )
