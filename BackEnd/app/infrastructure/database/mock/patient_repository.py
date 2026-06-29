import base64
from datetime import datetime, timezone
from typing import List, Optional

from app.core.patient_management.entities import (
    AneurysmAnalysisResult,
    Patient,
    Scan,
    ScanStatus,
)
from app.core.patient_management.repositories import Patients
from app.infrastructure.database.mock.data_layer import MockNoSQLDataLayer


class MockPatientRepository(Patients):
    def __init__(self, db: MockNoSQLDataLayer):
        self.db = db

    async def get_all(self) -> List[Patient]:
        return [
            Patient.model_validate(patient)
            for patient in self.db.patients.values()
        ]

    async def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        patient = self.db.patients.get(patient_id)
        if not patient:
            return None
        return Patient.model_validate(patient)

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
        ai_results: AneurysmAnalysisResult,
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

    async def get_all_pending_scans(self) -> List[Scan]:
        pending_scans = []
        for patient in self.db.patients.values():
            for scan_data in patient.get("scans", []):
                if scan_data.get("status") == "pending":
                    pending_scans.append(Scan.model_validate(scan_data))
        return pending_scans
    async def store_slice_image(
        self,
        scan_id: str,
        slice_index: int,
        base64_data: str,
    ) -> str:
        """
        Mock implementation of image storage.
        Stores the Base64 image in an in-memory dictionary and returns a reference.
        """
        # Generate a reference that looks realistic
        ref = f"mock://scans/{scan_id}/slice_{slice_index}.png"

        # Store the raw Base64 in the mock data layer's images dict
        if not hasattr(self.db, "images"):
            self.db.images = {}
        self.db.images[ref] = base64_data

        return ref
    async def get_slice_image(self, image_ref: str) -> Optional[bytes]:
        """Retrieve the raw binary image data given its reference."""
        if not hasattr(self.db, "images"):
            return None
        
        base64_str = self.db.images.get(image_ref)
        if base64_str is None:
            return None
        
        # Decode Base64 back to binary bytes
        try:
            return base64.b64decode(base64_str)
        except Exception:
            return None

