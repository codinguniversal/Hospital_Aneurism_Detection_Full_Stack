from typing import Dict, Any


class MockNoSQLDataLayer:
    """
    A dumb, in-memory data container that mimics a NoSQL database.
    It holds only raw dictionaries. All query logic is implemented in the repositories.
    """

    def __init__(self):
        print("Initializing Mock Database...")

        self.images: Dict[str, str] = {}

        self.users: Dict[str, Dict[str, Any]] = {
            "admin@hospital.org": {
                "employeeId": "ADMIN-01",
                "email": "admin@hospital.org",
                "password": "$2b$12$DXJYff7eXTk51xD/cmpgwOJhesLztTiZyPb90ffPwq5Ov3cNce2FK", #admin123
                "role": "Admin",
            },
            "user@example.com": {
                "employeeId": "USER-01",
                "email": "user@example.com",
                "password": "$2b$12$hrpmpdVQamB9yy98F9d.tuvWzCZkm7QGcJPxZKrTNTSOUFz8BuACm", #pasword123
                "role": "Doctor",
            },
        }

        self.patients: Dict[str, Dict[str, Any]] = {
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
                        "results": None,
                    }
                ],
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
                        "results": None,
                    }
                ],
            },
        }

        self.settings: Dict[str, Dict[str, Any]] = {
            "current_config": {
                "ai_api_url": "http://127.0.0.1:8001/analyze",
                "ai_timeout_limit": 60,
                "automatic_scan_start_hour": 8,
                "automatic_scan_end_hour": 17,
                "automatic_scan_interval": 60,
                "aneurysm_high_risk_threshold": 0.8,
                "aneurysm_medium_risk_threshold": 0.4,
            }
        }
