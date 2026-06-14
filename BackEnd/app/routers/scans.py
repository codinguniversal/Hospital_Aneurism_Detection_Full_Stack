import httpx
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.schemas.scan_schema import ScanAnalysisRequest
# from app.services.aneurysm_ai import run_aneurism_detection_ai

router = APIRouter(
    prefix="/scans",
    tags = ["AI Scanning"]
)
AI_API_URL = "http://127.0.0.1:8000/analyze"

@router.post("/analyze-manual")
async def run_manual_analysis(payload : ScanAnalysisRequest) :
    """
    endpoint triggered when Run Analysis button in front end table is pressed
    calls backend for the scans, then we call the ai service via network call  for results
    """
    async with httpx.AsyncClient as client :
        try: 
            files = {
                "file":(f"{}")
                }
    result = run_aneurism_detection_ai(payload.scan_id)
    mock_result = {
        "location_1_prob": 0.85,
        "location_2_prob": 0.12,
        "location_3_prob": 0.02,
        "location_4_prob": 0.13,
        "location_5_prob": 0.21,
        "location_6_prob": 0.01,
        "location_7_prob": 0.01,
        "location_8_prob": 0.01,
        "location_9_prob": 0.01,
        "location_10_prob": 0.01,
        "location_11_prob": 0.01,
        "location_12_prob": 0.01,
        "location_13_prob": 0.00,
        "total_probability": 0.85, # Total summary probability
        "urgency_label": "High"
    }
    return {
        "status": "completed",
        "patient_name" : payload.patient_name,
        "scan_id": payload.scan_id,
        "analysis_timestamp": datetime.now().isoformat(),
        "result" : mock_result
    }