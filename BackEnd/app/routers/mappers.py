
from typing import List

from app.schemas.patient_schema import PatientRecordResponseSchema
from app.schemas.user_schema import UserResponseSchema
from app.domain.entities import PatientEntity, ScanStatus, UserEntity


def patient_entities_to_records(high_threshold: float, mid_threshold: float ,patients: List[PatientEntity])-> List[PatientRecordResponseSchema] :
        results = []
        for patient in patients:
            if not patient.scans:
                continue  # Skip patients without scans
            latest_scan = patient.scans[0]  # Assuming the first scan is the latest; adjust if necessary
            urgency = latest_scan.urgency(high_threshold=high_threshold, mid_threshold=mid_threshold)
            results.append(
                PatientRecordResponseSchema(               
                    id= patient.id,
                    name=patient.patient_name,
                    scan_date=latest_scan.scan_date,
                    analyzed=latest_scan.status == ScanStatus.COMPLETED.value,
                    scan_analysis_date=latest_scan.scan_analysis_date,
                    urgency=urgency
                )
            )
                
        return results
def user_entities_to_user_response(users: List[UserEntity])->List[UserResponseSchema]:
    return [
        UserResponseSchema(
            id= user.employee_id,
            email= user.email,
            role = user.role
        )for user in users
    ] 