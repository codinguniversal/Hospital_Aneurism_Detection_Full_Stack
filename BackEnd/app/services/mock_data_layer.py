# mock data layer service for development
from typing import Any, Dict, Optional


class NoSQLDataLayer:
    def __init__(self):
        self._patients_collection = {
            "pat_001": {
                "id": "pat_001",
                "patient_name": "Alice Smith",
                "scans": [
                    {
                        "id": "scan_001",
                        "patient_id": "pat_001",
                        "scan_date": "2026-06-17",
                        "status": "Pending",
                        "binary_data": b"mock-dicom-bytes-for-alice",
                        "results": None
                    }
                ]
            },
            "pat_002": {
                "id": "pat_002",
                "patient_name": "Bob Jones",
                "scans": [
                    {
                        "id": "scan_002",
                        "patient_id": "pat_002",
                        "scan_date": "2026-06-17",
                        "status": "Pending",
                        "binary_data": b"mock-dicom-bytes-for-bob",
                        "results": None
                    }
                ]
            }
        }

        self._users_collection = {
            "admin@hospital.org": {
                "employeeId": "ADMIN-01",
                "email": "admin@hospital.org",
                "password": "admin123",
                "role": "admin"
            },
            "user@example.com": {
                "employeeId": "USER-01",
                "email": "user@example.com",
                "password": "password123",
                "role": "Doctor"
            }
        }
    async def get_user_credentials(self, identifier: str, is_admin: bool) -> Optional[Dict[str, Any]]:
        return self._users_collection.get(identifier)
 
_db_service = NoSQLDataLayer()
def get_data_layer():
    return _db_service