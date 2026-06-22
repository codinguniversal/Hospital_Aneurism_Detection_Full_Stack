from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.usecases.settings_use_cases.get_settings_use_case import GetSettingsUseCase
from app.domain.repositories import SettingsRepository
from app.domain.entities import PatientEntity
from app.usecases.patient_use_cases.get_patient_results_use_case import GetPatientResultsUseCase
from app.schemas.patient_schema import PatientRecordResponseSchema
from app.usecases.patient_use_cases.get_all_patients_use_case import GetAllPatientsUseCase
from app.dependencies import get_patient_records_use_case, get_patient_results_use_case, build_settings_repository, get_settings_use_case
from app.routers.mappers import patient_entities_to_records


router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/records", response_model=List[PatientRecordResponseSchema], status_code=status.HTTP_200_OK)
async def get_records(
    get_all_patients_use_case: GetAllPatientsUseCase = Depends(get_patient_records_use_case),
    get_settings_use_case: GetSettingsUseCase= Depends(get_settings_use_case)
):
    results = await get_all_patients_use_case.execute()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Patient Records were found")
    settings = await get_settings_use_case.execute()
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Settings were found") 
    
    high_threshold = settings.aneurysm_high_risk_threshold
    mid_threshold = settings.aneurysm_medium_risk_threshold
    patient_records = patient_entities_to_records(high_threshold= high_threshold, mid_threshold= mid_threshold, patients= results)
    return patient_records

@router.get("/{patient_id}", response_model=PatientEntity, status_code=status.HTTP_200_OK)
async def get_patient_results(
    patient_id: str,
    use_case: GetPatientResultsUseCase = Depends(get_patient_results_use_case)
):
    patient = await use_case.execute(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="The Patient was not found"
        )
    return patient