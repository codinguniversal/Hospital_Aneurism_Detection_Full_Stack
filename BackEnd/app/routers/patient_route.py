from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.patient_schema import PatientRecordResponse
from BackEnd.app.usecases.get_patient_records_use_case import GetPatientRecordsUseCase
from app.dependencies import get_patient_records_use_case


router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=List[PatientRecordResponse], status_code=status.HTTP_200_OK)
async def get_records(
    use_case: GetPatientRecordsUseCase = Depends(get_patient_records_use_case)
):
    return await use_case.execute()