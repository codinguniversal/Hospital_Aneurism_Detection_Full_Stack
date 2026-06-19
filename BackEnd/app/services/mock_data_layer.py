# mock data layer service for development
from typing import Any, Dict, Optional
from functools import lru_cache



class MockNoSQLDataLayer:
    def __init__(self):
        print("Initalizing Mock Database...")
        self._patients_collection = {
            "pat_001": {
                "id": "pat_001",
                "patient_name": "Alice Smith",
                "birth_date": "1990-05-15",
                "assigned_doc": "Dr. House",
                "scans": [
                    {
                        "id": "scan_001",
                        "patient_id": "pat_001",
                        "scan_date": "2026-06-17T10:00:00",
                        "status": "pending",
                        "img_file_path": "/data/scans/scan_001.dcm",
                        "results": None
                    }
                ]
                },
            "pat_002": {
                "id": "pat_002",
                "patient_name": "Bob Jones",
                "birth_date": "1985-11-23",
                "assigned_doc": "Dr. Wilson",
                "scans": [
                    {
                        "id": "scan_002",
                        "patient_id": "pat_002",
                        "scan_date": "2026-06-17T11:30:00",
                        "status": "pending",
                        "img_file_path": "/data/scans/scan_002.dcm",
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
        self._settings_collection = {
            "current_config": {
                "ai_api_url": "http://127.0.0.1:8001/analyze",
                "ai_timeout_limit": 60,
                "automatic_scan_start_hour": 8,
                "automatic_scan_end_hour": 17,
                "automatic_scan_interval": 60,
                "aneurysm_high_risk_threshold": 0.8,
                "aneurysm_medium_risk_threshold": 0.4
            }
        }
    async def get_user_credentials(self, identifier: str, is_admin: bool) -> Optional[Dict[str, Any]]:
        return self._users_collection.get(identifier)
@lru_cache()
def get_data_layer()->MockNoSQLDataLayer:
    return MockNoSQLDataLayer()