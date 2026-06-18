# Inside backend/app/domain/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import UserEntity, PatientEntity

class UserRepository(ABC):
    @abstractmethod
    async def get_by_identifier(self, identifier: str) -> Optional[UserEntity]:
        """Fetch complete UserEntity by employee_id or return None"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Fetch details of a specific staff user based on their login email"""
        pass

    @abstractmethod
    async def add_user(self, user: UserEntity) -> None:
        """Persist a new user (admin/doctor) in the data layer"""
        pass

class PatientRepository(ABC):
    @abstractmethod
    async def get_all_patients(self) -> List[PatientEntity]:
        """Returns all patients in the hospital system (including pre-existing scans)"""
        pass

    @abstractmethod
    async def get_patient_by_id(self, patient_id: str) -> Optional[PatientEntity]:
        """Fetch details of a specific patient along with their pre-existing scans"""
        pass

    @abstractmethod
    async def get_scan_file_path(self, scan_id: str) -> Optional[str]:
        """
        Traverses patient documents to retrieve the absolute disk storage file path 
        pointing to the patient's raw or compressed (.zip/.dcm) scan archive.
        """
        pass

    @abstractmethod
    async def update_scan_results(self, patient_id: str, scan_id: str, status: str, ai_results: dict) -> bool:
        """Atomically updates the pre-existing scan state and diagnostic probability values"""
        pass