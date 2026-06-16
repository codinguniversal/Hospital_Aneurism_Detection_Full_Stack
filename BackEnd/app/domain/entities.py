from typing import Dict

from pydantic import BaseModel

class UserEntity(BaseModel):
    employee_id: str
    email: str
    password: str
    role: str

class ScanEntity(BaseModel):
    id: str
    patient_name: str
    status: str
    binary_data: str
    results: Dict