from datetime import datetime, timezone
from typing import List, Optional

from app.domain.entities import AneurysmAnalysisResultEntity, PatientEntity, ScanEntity
from app.domain.repositories import PatientRepository
from app.services.mock_data_layer import MockNoSQLDataLayer
from app.domain.entities import ScanStatus

class MockPatientRepository(PatientRepository):
    def __init__(self, db: MockNoSQLDataLayer):
        self.db = db

    async def get_all_patients(self) -> List[PatientEntity]:
        return [
            PatientEntity.model_validate(patient)
            for patient in self.db._patients_collection.values()
        ]

    async def get_patient_by_id(self, patient_id: str) -> Optional[PatientEntity]:
        patient = self.db._patients_collection.get(patient_id)
        if not patient:
            return None
        return PatientEntity.model_validate(patient)

    async def get_scan_file_path(self, scan_id: str) -> Optional[str]:
        """Return the stored file path for a given scan_id."""
        for patient in self.db._patients_collection.values():
            for scan in patient["scans"]:
                if scan["id"] == scan_id:
                    return scan.get("img_file_path")
        return None
    async def get_scan_file(self, scan_id: str) -> Optional[bytes]:
        """
        Returns the raw binary bytes of the scan file for a given scan_id.
        In the mock, we return dummy bytes or read a real file if the path exists.
        """
        for patient in self.db._patients_collection.values():
            for scan in patient.get("scans", []):
                if scan["id"] == scan_id:
                    file_path = scan.get("img_file_path")
                    if file_path:
                        # In a real mock, you could read the actual file:
                        # with open(file_path, "rb") as f:
                        #     return f.read()
                        # But since this is a mock, returning dummy bytes is safe
                        return b"mock binary data for scan"
        return None
    async def update_scan_results(
        self,
        scan_id: str,
        ai_results: AneurysmAnalysisResultEntity
    ) -> bool:
        """
        Updates the scan status to 'Completed' and stores the AI results.
        Finds the scan by scanning across all patients (mock implementation).
        """
        # Convert the domain entity to a plain dict for storage
        results_dict = ai_results.model_dump()

        for patient in self.db._patients_collection.values():
            for scan in patient.get("scans", []):
                if scan["id"] == scan_id:
                    scan["status"] = ScanStatus.COMPLETED.value
                    scan["results"] = results_dict
                    scan["scan_analysis_date"] = datetime.now(timezone.utc).isoformat()
                    return True
        return False
    async def get_all_pending_scans(self) -> List[ScanEntity]:
        """
        Retrieves all scans that have not been analyzed yet (status == 'pending').
        """
        pending_scans = []
        for patient in self.db._patients_collection.values():
            for scan_data in patient.get("scans", []):
                if scan_data.get("status") == "pending":
                    # Pydantic's model_validate handles string -> datetime conversion automatically
                    pending_scans.append(ScanEntity.model_validate(scan_data))
        return pending_scans