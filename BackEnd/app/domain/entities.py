from typing import Dict, List, Optional
from datetime import datetime

class UserEntity:
    def __init__(self, employee_id: str, email: str, password: str, role: str):
        self.employee_id = employee_id
        self.email = email
        self.password = password
        self.role = role  # admin/ doctor

class ScanEntity:
    def __init__(self, id: str, patient_id: str, scan_date: datetime, status: str, img_file_path: str, results: Optional[Dict] = None):
        self.id = id
        self.scan_date = scan_date or datetime.utcnow()
        self.status = status  # Pending /Completed /Failed
        self.img_file_path = img_file_path  
        self.results = results or {}  

class PatientEntity:
    def __init__(self, id: str, patient_name: str, birth_date: str, assigned_doc: str, medical_history: List[str] = None, scans: List[ScanEntity] = None):
        self.id = id
        self.patient_name = patient_name
        self.birth_date = birth_date  
        self.assigned_doc = assigned_doc  
        self.medical_history = medical_history or []
        self.scans = scans or []

    def add_scan(self, scan: ScanEntity):
        """Domain Rule: Ensure duplicate scan IDs aren't allowed"""
        if any(s.id == scan.id for s in self.scans):
            raise ValueError("Scan ID already exists for this patient")
        self.scans.append(scan)