from datetime import datetime
from typing import List, Optional

from app.domain.entities import PatientEntity, ScanEntity
from app.domain.repositories import PatientRepository
from app.services.mock_data_layer import MockNoSQLDataLayer

class MockPatientRepository(PatientRepository):
    def __init__(self, data_layer: MockNoSQLDataLayer):
        self.data_layer = data_layer

    async def get_all_patients(self) -> List[PatientEntity]:
        return [
            PatientEntity.model_validate(patient)
            for patient in self.data_layer._patients_collection.values()
        ]

    async def get_patient_by_id(self, patient_id: str) -> Optional[PatientEntity]:
        patient = self.data_layer._patients_collection.get(patient_id)
        if not patient:
            return None
        return PatientEntity.model_validate(patient)

    async def get_scan_file_path(self, scan_id: str) -> Optional[str]:
        """Return the stored file path for a given scan_id."""
        for patient in self.data_layer._patients_collection.values():
            for scan in patient["scans"]:
                if scan["id"] == scan_id:
                    return scan.get("img_file_path")
        return None

    async def update_scan_results(
        self, patient_id: str, scan_id: str, status: str, ai_results: dict
    ) -> bool:
        """Update the scan status and results for a specific patient’s scan."""
        patient = self.data_layer._patients_collection.get(patient_id)
        if not patient:
            return False
        for scan in patient["scans"]:
            if scan["id"] == scan_id:
                scan["status"] = status
                scan["results"] = ai_results
                return True
        return False