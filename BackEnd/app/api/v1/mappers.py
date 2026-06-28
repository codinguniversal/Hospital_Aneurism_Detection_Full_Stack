
from typing import List

from app.api.v1.schemas.patient_schema import PatientRecordResponseSchema
from app.api.v1.schemas.user_schema import UserResponseSchema
from app.core.patient_management.entities import PatientEntity, ScanStatus
from app.modules.identity_access.entities import UserEntity


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
                    scan_id= latest_scan.id,
                    name=patient.patient_name,
                    assigned_doc=patient.assigned_doc,
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