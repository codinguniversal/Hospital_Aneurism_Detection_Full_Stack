from datetime import datetime, timezone
from typing import List, Optional

from app.core.patient_management.entities import (
    AneurysmAnalysisResultEntity,
    PatientEntity,
    ScanEntity,
    ScanStatus,
)
from app.core.patient_management.repositories import PatientRepository
from app.infrastructure.database.mock.data_layer import MockNoSQLDataLayer


class MockPatientRepository(PatientRepository):
    def __init__(self, db: MockNoSQLDataLayer):
        self.db = db

    async def get_all_patients(self) -> List[PatientEntity]:
        return [
            PatientEntity.model_validate(patient)
            for patient in self.db.patients.values()
        ]

    async def get_patient_by_id(self, patient_id: str) -> Optional[PatientEntity]:
        patient = self.db.patients.get(patient_id)
        if not patient:
            return None
        return PatientEntity.model_validate(patient)

    async def get_scan_file_path(self, scan_id: str) -> Optional[str]:
        for patient in self.db.patients.values():
            for scan in patient.get("scans", []):
                if scan["id"] == scan_id:
                    return scan.get("img_file_path")
        return None

    async def get_scan_file(self, scan_id: str) -> Optional[bytes]:
        for patient in self.db.patients.values():
            for scan in patient.get("scans", []):
                if scan["id"] == scan_id:
                    file_path = scan.get("img_file_path")
                    if file_path:
                        return b"mock binary data for scan"
        return None

    async def update_scan_results(
        self,
        scan_id: str,
        ai_results: AneurysmAnalysisResultEntity,
    ) -> bool:
        results_dict = ai_results.model_dump()

        for patient in self.db.patients.values():
            for scan in patient.get("scans", []):
                if scan["id"] == scan_id:
                    scan["status"] = ScanStatus.COMPLETED.value
                    scan["results"] = results_dict
                    scan["scan_analysis_date"] = datetime.now(timezone.utc).isoformat()
                    return True
        return False

    async def get_all_pending_scans(self) -> List[ScanEntity]:
        pending_scans = []
        for patient in self.db.patients.values():
            for scan_data in patient.get("scans", []):
                if scan_data.get("status") == "pending":
                    pending_scans.append(ScanEntity.model_validate(scan_data))
        return pending_scans
