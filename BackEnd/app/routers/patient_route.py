from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from BackEnd.app.domain.entities import PatientEntity
from BackEnd.app.usecases.get_patient_results_use_case import GetPatientResultsUseCase
from app.schemas.patient_schema import PatientRecordResponse
from BackEnd.app.usecases.get_patient_records_use_case import GetPatientRecordsUseCase
from app.dependencies import get_patient_records_use_case


router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/records", response_model=List[PatientRecordResponse], status_code=status.HTTP_200_OK)
async def get_records(
    use_case: GetPatientRecordsUseCase = Depends(get_patient_records_use_case)
):
    return await use_case.execute()
@router.get("/{patiend_id}", response_model= PatientEntity, status_code= status.HTTP_200_OK)
async def get_patient_results(
    patient_id: str,
    use_case: GetPatientResultsUseCase
):
    patient = await use_case.execute(patient_id)
    if not patient:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="The Patient was not found")
    return patient