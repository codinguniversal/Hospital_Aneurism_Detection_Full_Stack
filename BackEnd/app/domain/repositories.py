from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import HttpUrl
from app.domain.entities import ScanEntity, SettingsEntity, UserEntity, PatientEntity, AneurysmAnalysisResultEntity

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
    @abstractmethod
    async def get_all_users(self)->List[UserEntity]:
        """Fetches all users"""
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
    async def get_scan_file(self, scan_id: str) -> Optional[bytes]:
        """
        Returns the raw binary bytes data of the scan file for a given scan_id.
        """
        pass
    @abstractmethod
    async def update_scan_results(self,  scan_id: str, ai_results:AneurysmAnalysisResultEntity) -> bool:
        """Atomically updates the pre-existing scan state and diagnostic probability values"""
        pass
    @abstractmethod
    async def get_all_pending_scans(self) -> List[ScanEntity]:
        """retrieves all scans that have not been analyzed yet"""
        pass

class SettingsRepository(ABC):
    @abstractmethod
    async def get_settings(self) -> SettingsEntity:
        """Fetches the current system settings (e.g., AI thresholds)
        This method should implement caching to minimize data layer calls, as settings are read frequently but updated rarely."""
        pass
    @abstractmethod
    async def update_settings(self, settings: SettingsEntity) -> None:
        """Updates the system settings (e.g., AI thresholds)
        This method should ensure that the cache is updated accordingly after persisting changes to the data layer.
        """
        pass
