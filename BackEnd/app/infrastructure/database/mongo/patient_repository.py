import base64
from datetime import datetime, date, timezone
import os
from pathlib import Path
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.patient_management.entities import AneurysmAnalysisResult, Patient, Scan
from app.core.patient_management.repositories import Patients as IPatientRepository

class MongoPatientRepository(IPatientRepository):
    def __init__(
            self, 
            db: AsyncIOMotorDatabase,
            storage_base_dir: str,
            slice_meta_collection_name: str
            ):
        self.collection = db["patients"]
        self.slice_meta_collection = db[slice_meta_collection_name]
        self.storage_base_dir = storage_base_dir

    def _scan_to_document(self, scan: Scan) -> dict:
        return {
            "id": scan.id,
            "scan_date": scan.scan_date,
            "status": scan.status,
            "img_file_path": scan.img_file_path,
            "results": scan.results.model_dump() if scan.results else None,
        }

    def _entity_to_document(self, patient: Patient) -> dict:
        return {
            "_id": patient.id,
            "patient_name": patient.patient_name,
            "birth_date": patient.birth_date,
            "assigned_doc": patient.assigned_doc,
            "medical_history": patient.medical_history,
            "scans": [self._scan_to_document(s) for s in patient.scans],
        }

    def _document_to_entity(self, doc: dict) -> Patient:
        scans_entities = []

        for s in doc.get("scans", []):
            results_dict = s.get("results")

            if results_dict == {}:
                results_obj = None
            else:
                results_obj = AneurysmAnalysisResult(**results_dict) if results_dict else None

            raw_status = s.get("status", "pending").lower()

            raw_scan_date = s.get("scan_date")
            if isinstance(raw_scan_date, str):
                scan_date_obj = datetime.fromisoformat(raw_scan_date.replace("Z", "+00:00"))
            else:
                scan_date_obj = raw_scan_date

            scans_entities.append(
                Scan(
                    id=s["id"],
                    scan_date=scan_date_obj,
                    status=raw_status,
                    img_file_path=s["img_file_path"],
                    scan_analysis_date=s.get("scan_analysis_date"),
                    results=results_obj,
                )
            )

        raw_birth_date = doc["birth_date"]
        if isinstance(raw_birth_date, str):
            birth_date_obj = date.fromisoformat(raw_birth_date)
        else:
            birth_date_obj = raw_birth_date

        return Patient(
            id=doc["_id"],
            patient_name=doc["patient_name"],
            birth_date=birth_date_obj,
            assigned_doc=doc["assigned_doc"],
            medical_history=doc.get("medical_history", []),
            scans=scans_entities,
        )

    async def get_all(self) -> List[Patient]:
        patients_entities = []
        cursor = self.collection.find({})
        async for doc in cursor:
            patients_entities.append(self._document_to_entity(doc))
        return patients_entities

    async def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        doc = await self.collection.find_one({"_id": patient_id})

        if not doc:
            return None

        return self._document_to_entity(doc)

    async def get_scan_file(self, scan_id: str) -> Optional[bytes]:
        doc = await self.collection.find_one({"scans.id": scan_id})
        if not doc:
            return None

        file_path = None
        for s in doc.get("scans", []):
            if s.get("id") == scan_id:
                file_path = s.get("img_file_path")
                break

        if not file_path:
            raise FileNotFoundError(
                f"Scan {scan_id} has no DICOM ZIP path configured in MongoDB."
            )

        # MongoDB stores paths as strings. Normalize mixed slash styles,
        # surrounding quotes, environment variables, and relative components.
        normalized_path = Path(
            os.path.normpath(os.path.expandvars(str(file_path).strip().strip('"')))
        ).expanduser()

        if not normalized_path.is_file():
            raise FileNotFoundError(
                f"DICOM ZIP for scan {scan_id} does not exist at "
                f"'{normalized_path}'. Update scans.$.img_file_path with the full Windows path."
            )

        with normalized_path.open("rb") as archive_file:
            return archive_file.read()

    async def update_scan_results(self, scan_id: str, ai_results: AneurysmAnalysisResult) -> bool:
        results = ai_results.model_dump()
        update_result = await self.collection.update_one(
            {"scans.id": scan_id},
            {
                "$set": {
                    "scans.$.status": "Completed",
                    "scans.$.scan_analysis_date": datetime.now(timezone.utc),
                    "scans.$.results": results,
                }
            },
        )
        return update_result.modified_count > 0

    async def get_all_pending_scans(self) -> List[Scan]:
        pipeline = [
            {"$unwind": "$scans"},
            {"$match": {"scans.status": "pending"}},
            {"$replaceRoot": {"newRoot": "$scans"}},
        ]

        pending_scans = []
        cursor = self.collection.aggregate(pipeline)

        async for scan_data in cursor:
            pending_scans.append(Scan.model_validate(scan_data))

        return pending_scans

    async def store_slice_image(
            self,
            scan_id: str,
            slice_index: int,
            base64_data: str,
            image_kind: str = "overlay",
            ) -> str:
        """
        Saves the binary decoded highlighted AI slice directly onto the server disk storage,
        tracks the file path metadata inside MongoDB, and returns a absolute file path reference.
        """
        # Clean data URL string headers if sent (e.g., 'data:image/png;base64,')
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        # Decode base64 down to raw binary image data
        binary_image_bytes = base64.b64decode(base64_data)

        # Build clean directory structure per scan for efficient os directory traversal
        scan_directory = os.path.join(self.storage_base_dir, scan_id)
        os.makedirs(scan_directory, exist_ok=True)

        # Generate absolute filename for the pinpointed frame slice
        safe_image_kind = "raw" if image_kind == "raw" else "overlay"
        file_name = f"{safe_image_kind}_slice_{slice_index}.png"
        target_file_path = os.path.normpath(os.path.join(scan_directory, file_name))

        # Write data natively to host file system
        with open(target_file_path, "wb") as file_out:
            file_out.write(binary_image_bytes)

        # Save metadata index pointer inside MongoDB.
        # This keeps database sizes small while allowing quick lookups via the path string.
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

        # Return the verified file path reference string for downstream consumption
        return target_file_path

    async def get_slice_image(self, slice_ref: str) -> Optional[bytes]:
        """
        Reads the highlight binary bytes straight from the disk path.
        Returns None if the file reference is unlinked or deleted from physical disk.
        """
        # Verify that the path string exists on disk before attempting to stream it
        if not slice_ref or not os.path.exists(slice_ref):
            print(f"[REPO WARNING] Highlight slice reference target missing on disk: {slice_ref}")
            return None

        try:
            with open(slice_ref, "rb") as file_in:
                return file_in.read()
        except Exception as e:
            print(f"[REPO ERROR] OS exception encountered streaming file from disk: {e}")
            return None
