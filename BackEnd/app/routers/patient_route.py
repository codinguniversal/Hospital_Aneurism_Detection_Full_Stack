from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.domain.repositories import SettingsRepository
from app.domain.entities import PatientEntity
from app.usecases.patient_use_cases.get_patient_results_use_case import GetPatientResultsUseCase
from app.schemas.patient_schema import PatientRecordResponseSchema
from BackEnd.app.usecases.patient_use_cases.get_all_patients_use_case import GetAllPatientsUseCase
from app.dependencies import get_patient_records_use_case, get_patient_results_use_case, build_settings_repository
from app.routers.patient_mappers import patient_entitities_to_records


router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/records", response_model=List[PatientRecordResponseSchema], status_code=status.HTTP_200_OK)
async def get_records(
    use_case: GetAllPatientsUseCase = Depends(get_patient_records_use_case),
    settings_repo: SettingsRepository= Depends(build_settings_repository)
):
    results = await use_case.execute()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Patient Records were found")
    settings = await settings_repo.get_settings()
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Settings were found") 
    
    high_threshold = settings.aneurysm_high_risk_threshold
    mid_threshold = settings.aneurysm_medium_risk_threshold
    patient_records =  patient_entitities_to_records(high_threshold= high_threshold, mid_threshold= mid_threshold, patients= results)
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