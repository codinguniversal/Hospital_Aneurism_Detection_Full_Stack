import base64
import os
import aiofiles
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
        image_kind: str = "overlay",
    ) -> str:
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        binary_image_bytes = base64.b64decode(base64_data)

        scan_directory = os.path.join(self.storage_base_dir, scan_id)
        os.makedirs(scan_directory, exist_ok=True)

        safe_image_kind = "raw" if image_kind == "raw" else "overlay"
        file_name = f"{safe_image_kind}_slice_{slice_index}.png"
        target_file_path = os.path.normpath(os.path.join(scan_directory, file_name))

        # FIX: Native non-blocking file writing
        async with aiofiles.open(target_file_path, "wb") as file_out:
            await file_out.write(binary_image_bytes)

        # Motor MongoDB update stays async
        await self.slice_meta_collection.update_one(
            {"_id": target_file_path},
            {
                "$set": {
                    "scan_id": scan_id,
                    "slice_index": slice_index,
                    "image_kind": safe_image_kind,
                    "stored_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        return target_file_path


    async def get_slice_image(self, slice_ref: str) -> Optional[bytes]:
        if not slice_ref or not os.path.exists(slice_ref):
            print(f"[REPO WARNING] Highlight slice reference target missing on disk: {slice_ref}")
            return None

        try:
            # FIX: Native non-blocking file reading
            async with aiofiles.open(slice_ref, "rb") as file_in:
                return await file_in.read()
        except Exception as e:
            print(f"[REPO ERROR] OS exception encountered streaming file from disk: {e}")
            return None
