from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.domain.entities import PatientEntity
from app.usecases.patient_use_cases.get_patient_results_use_case import GetPatientResultsUseCase
from app.schemas.patient_schema import PatientRecordResponse
from app.usecases.patient_use_cases.get_patient_records_use_case import GetPatientRecordsUseCase
from app.dependencies import get_patient_records_use_case, get_patient_results_use_case


router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/records", response_model=List[PatientRecordResponse], status_code=status.HTTP_200_OK)
async def get_records(
    use_case: GetPatientRecordsUseCase = Depends(get_patient_records_use_case)
):
    patients = await use_case.execute()
    if not patients:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="No Patient Records  were  found")
    return [
            PatientRecordResponse(
                id=patient.id,
                name=patient.patient_name,
                image_date=patient.scans[0].scan_date,
                analyzed=patient.scans[0].status == "Completed",
                urgency= patient.scans[0].urgency
            )
            for  patient in patients
        ]
@router.get("/{patient_id}", response_model= PatientEntity, status_code= status.HTTP_200_OK)
async def get_patient_results(
    patient_id: str,
    use_case: GetPatientResultsUseCase = Depends(get_patient_results_use_case)
):
    patient = await use_case.execute(patient_id)
    if not patient:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="The Patient was not found")
    return patient