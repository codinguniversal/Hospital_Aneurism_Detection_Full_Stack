from datetime import datetime, date
import os
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.patient_management.entities import AneurysmAnalysisResultEntity, PatientEntity, ScanEntity
from app.core.patient_management.repositories import PatientRepository as IPatientRepository


class MongoPatientRepository(IPatientRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["patients"]

    def _scan_to_document(self, scan: ScanEntity) -> dict:
        return {
            "id": scan.id,
            "scan_date": scan.scan_date,
            "status": scan.status,
            "img_file_path": scan.img_file_path,
            "results": scan.results.model_dump() if scan.results else None,
        }

    def _entity_to_document(self, patient: PatientEntity) -> dict:
        return {
            "_id": patient.id,
            "patient_name": patient.patient_name,
            "birth_date": patient.birth_date,
            "assigned_doc": patient.assigned_doc,
            "medical_history": patient.medical_history,
            "scans": [self._scan_to_document(s) for s in patient.scans],
        }

    def _document_to_entity(self, doc: dict) -> PatientEntity:
        scans_entities = []

        for s in doc.get("scans", []):
            results_dict = s.get("results")

            if results_dict == {}:
                results_obj = None
            else:
                results_obj = AneurysmAnalysisResultEntity(**results_dict) if results_dict else None

            raw_status = s.get("status", "pending").lower()

            raw_scan_date = s.get("scan_date")
            if isinstance(raw_scan_date, str):
                scan_date_obj = datetime.fromisoformat(raw_scan_date.replace("Z", "+00:00"))
            else:
                scan_date_obj = raw_scan_date

            scans_entities.append(
                ScanEntity(
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

        return PatientEntity(
            id=doc["_id"],
            patient_name=doc["patient_name"],
            birth_date=birth_date_obj,
            assigned_doc=doc["assigned_doc"],
            medical_history=doc.get("medical_history", []),
            scans=scans_entities,
        )

    async def get_all_patients(self) -> List[PatientEntity]:
        patients_entities = []
        cursor = self.collection.find({})
        async for doc in cursor:
            patients_entities.append(self._document_to_entity(doc))
        return patients_entities

    async def get_patient_by_id(self, patient_id: str) -> Optional[PatientEntity]:
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

        if not file_path or not os.path.exists(file_path):
            print(f"[REPO ERROR] File missing on storage disk at: {file_path}")
            return None

        with open(file_path, "rb") as archive_file:
            return archive_file.read()

    async def update_scan_results(self, scan_id: str, ai_results: AneurysmAnalysisResultEntity) -> bool:
        results = ai_results.model_dump()
        update_result = await self.collection.update_one(
            {"scans.id": scan_id},
            {
                "$set": {
                    "scans.$.status": "Completed",
                    "scans.$.results": results,
                }
            },
        )
        return update_result.modified_count > 0

    async def get_all_pending_scans(self) -> List[ScanEntity]:
        pipeline = [
            {"$unwind": "$scans"},
            {"$match": {"scans.status": "pending"}},
            {"$replaceRoot": {"newRoot": "$scans"}},
        ]

        pending_scans = []
        cursor = self.collection.aggregate(pipeline)

        async for scan_data in cursor:
            pending_scans.append(ScanEntity.model_validate(scan_data))

        return pending_scans
