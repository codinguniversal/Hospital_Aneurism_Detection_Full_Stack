from typing import List, Optional

from app.domain.entities import PatientEntity, ScanEntity
from app.domain.repositories import PatientRepository
from app.services.mock_data_layer import  NoSQLDataLayer

class MockPatientRepository(PatientRepository):
    def __init__(self, data_layer: NoSQLDataLayer):
        self.data_layer = data_layer
    async def get_all_patients(self) -> List[PatientEntity]:
        return [
            PatientEntity.model_validate(patient)
            for patient in self.data_layer._patients_collection.values()
        ]
    async def get_scan_binary_data(self, scan_id: str) -> Optional[bytes]:
        for patient in self.data_layer._patients_collection.values():
            for scan in patient["scans"]:
                if scan["id"] == scan_id:
                    return scan["binary_data"]
        return None

    async def get_all_pending_scans(self) -> List[ScanEntity]:
        pending = []
        for patient in self.data_layer._patients_collection.values():
            for scan in patient["scans"]:
                if scan["status"] == "Pending":
                    pending.append(
                        ScanEntity(
                            id=scan["id"],
                            patient_id=scan.get("patient_id", "UNKNOWN"), # Optional: add defaults if needed
                            scan_date=scan.get("scan_date", ""),
                            status=scan.get("status", "Pending"),
                            binary_data=scan.get("binary_data", b""),
                            results=scan.get("results") or {}
                        )
                    )
        return pending

    async def update_scan_results(self, scan_id: str, results: dict) -> None:
        for patient in self.data_layer._patients_collection.values():
            for scan in patient["scans"]:
                if scan["id"] == scan_id:
                    scan["status"] = "Completed"
                    scan["results"] = results
                    return
    async def get_patient_by_id(self, patient_id: str) -> Optional[PatientEntity]:
        patient = self.data_layer._patients_collection.get(patient_id)

        if not patient:
            return None

        return PatientEntity.model_validate(patient)