from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

# Core Domains & Use Cases
from app.core.patient_management.entities import PatientEntity
from app.core.patient_management.use_cases import GetAllPatientsUseCase, GetPatientResultsUseCase
from app.modules.system_settings.use_cases import GetSettingsUseCase

# Infrastructure & Security
from app.dependencies import RoleChecker

# Presentation Layer (Schemas & Mappers)
from app.api.v1.schemas.patient_schema import PatientRecordResponseSchema
from app.api.v1.mappers import patient_entities_to_records

# Dependency Builders
from app.dependencies import (
    build_get_patient_records_use_case, 
    build_get_patient_results_use_case, 
    build_get_settings_use_case
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get(
    "/records", 
    response_model=List[PatientRecordResponseSchema], 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker(["Radiologist", "Doctor"]))] 
)
async def get_records(
    get_all_patients_use_case: GetAllPatientsUseCase = Depends(build_get_patient_records_use_case),
    get_settings_use_case: GetSettingsUseCase = Depends(build_get_settings_use_case)
):
    results = await get_all_patients_use_case.execute()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No Patient Records were found"
        )
        
    settings = await get_settings_use_case.execute()
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No Settings were found"
        ) 
    
    patient_records = patient_entities_to_records(
        high_threshold=settings.aneurysm_high_risk_threshold, 
        mid_threshold=settings.aneurysm_medium_risk_threshold, 
        patients=results
    )
    return patient_records


@router.get(
    "/{patient_id}", 
    response_model=PatientEntity, 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker(["Radiologist", "Doctor", "Admin"]))]  
)
async def get_patient_results(
    patient_id: str,
    use_case: GetPatientResultsUseCase = Depends(build_get_patient_results_use_case)
):
    patient = await use_case.execute(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="The Patient was not found"
        )
    return patient