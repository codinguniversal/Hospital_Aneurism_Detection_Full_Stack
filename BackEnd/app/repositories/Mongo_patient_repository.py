from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.entities import PatientEntity, ScanEntity

class PatientRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        # We pass the database instance (CAD_DB) initialized in main.py
        self.collection = db["patients"]

    #Helpers for data translation
    def _scan_to_document(self, scan: ScanEntity) -> dict:
        """Convert a Scan Domain Entity into a MongoDB dict"""
        return {
            "id": scan.id,
            "scan_date": scan.scan_date,
            "status": scan.status,
            "img_file_path": scan.img_file_path,
            "results": scan.results
        }

    def _entity_to_document(self, patient: PatientEntity) -> dict:
        """Convert a Patient Domain Entity into a MongoDB dict"""
        return {
            "_id": patient.id,  
            "patient_name": patient.patient_name,
            "birth_date": patient.birth_date,
            "assigned_doc": patient.assigned_doc,
            "medical_history": patient.medical_history,
            "scans": [self._scan_to_document(s) for s in patient.scans]
        }

    def _document_to_entity(self, doc: dict) -> PatientEntity:
        """Convert a MongoDB dict back into a pure Patient Domain Entity"""
        scans_entities = []
        for s in doc.get("scans", []):
            scans_entities.append(
                ScanEntity(
                    id=s["id"],
                    scan_date=s["scan_date"],
                    status=s["status"],
                    img_file_path=s["img_file_path"],
                    results=s.get("results")
                )
            )
        
        return PatientEntity(
            id=doc["_id"], 
            patient_name=doc["patient_name"],
            birth_date=doc["birth_date"],
            assigned_doc=doc["assigned_doc"],
            medical_history=doc.get("medical_history", []),
            scans=scans_entities
        )
    
    async def get_all_patients(self) -> List[PatientEntity]:
        """Fetch all patient documents from MongoDB and map them to Domain Entities"""
        patients_entities = []
        cursor = self.collection.find({})
        async for doc in cursor:
            patients_entities.append(self._document_to_entity(doc))
        return patients_entities
    
    async def get_patient_by_id(self, patient_id:str) -> Optional[PatientEntity]:
        doc = await self.collection.find_one({"_id" : patient_id})
        if not doc:
            return None
        return self._document_to_entity(doc)
    
    
    async def update_scan_results(self,patient_id: str, scan_id: str, status: str, ai_results: dict) -> bool:

        results = await self.collection.update_one(
            {"_id": patient_id, "scans.id" : scan_id},
            {
                "$set" : {
                    "scans.$status" : status, # '$' operator tells MongoDb to modify only matching item
                    "scans.$.results": ai_results
                }
            }
        )
        return results.modified_count > 0
