# mock data layer service for development
from typing import Any, Dict, Optional


class NoSQLDataLayer:
    def __init__(self):
        self._scans_collection = {
            "scan_001": {
                "id": "scan_001",
                "patient_name": "Alice Smith",
                "status": "Pending",
                "binary_data": b"mock-dicom-bytes-for-alice",
                "results": None
            },
            "scan_002": {
                "id": "scan_002",
                "patient_name": "Bob Jones",
                "status": "Pending",
                "binary_data": b"mock-dicom-bytes-for-bob",
                "results": None
            },
            "scan_003": {
                "id": "scan_003",
                "patient_name": "Charlie Brown",
                "status": "Completed",
                "binary_data": b"mock-dicom-bytes-for-charlie",
                "results": {"total_probability": 0.02, "urgency_label": "Low"}
            }
        }
        self._users_collection = {
            "admin@hospital.org": {
                "employeeId": "ADMIN-01",
                "email": "admin@hospital.org",
                "password": "admin123",
                "role": "admin",
                "mock_token": "mock-secure-jwt-token-xyz"
            },
            "123456": {
                "employeeId": "123456",
                "email": "dr.ahmed@hospital.org",
                "password": "doctor123",
                "role": "doctor",
                "mock_token": "mock-secure-jwt-token-abc"
            }
        }
    async def get_user_credentials(self, identifier: str, is_admin: bool) -> Optional[Dict[str, Any]]:
        return self._users_collection.get(identifier)
    async def get_scan_binary_data(self, scan_id: str)-> bytes | None:
        scan = self._scans_collection.get(scan_id)
        return scan["binary_data"] if scan else None
    
    async def get_scan_by_id(self, scan_id: str):
        return self._scans_collection.get(scan_id)

    async def get_all_pending_scans(self):
        return [scan for scan in self._scans_collection.values() if scan["status"] == "Pending"]
    
    async def update_scan_results(self, scan_id: str, results: dict):
        if scan_id in self._scans_collection:
            self._scans_collection[scan_id]["status"] = "Completed"
            self._scans_collection[scan_id]["results"] = results
            print(f"DB State Change: {scan_id} marked as Completed in NoSQL mock storage.")
            return True
        return False
    
_db_service = NoSQLDataLayer()
def get_data_layer():
    return _db_service