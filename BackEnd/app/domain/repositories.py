# Inside backend/app/domain/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional, AsyncIterator
from app.domain.entities import SettingsEntity, UserEntity, PatientEntity, AneurysmAnalysisResultEntity

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
    async def get_scan_file(self, scan_id: str) -> Optional[bytes]:
        """
        Returns the raw binary bytes data of the scan file for a given scan_id.
        """
        pass
    @abstractmethod
    async def update_scan_results(self,  scan_id: str, ai_results:AneurysmAnalysisResultEntity) -> bool:
        """Atomically updates the pre-existing scan state and diagnostic probability values"""
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
    @property
    @abstractmethod
    async def ai_api_url(self) -> str:
        """Returns the current AI API URL from the settings"""
        pass

    @property
    @abstractmethod
    async def ai_timeout_limit(self) -> int:
        """Returns the current AI timeout limit from the settings"""
        pass
    @property
    @abstractmethod
    async def automatic_scan_start_hour(self) -> int:
        """Returns the current automatic scan start hour from the settings"""
        pass
    @property
    @abstractmethod
    async def automatic_scan_end_hour(self) -> int:
        """Returns the current automatic scan end hour from the settings"""
        pass
    @property
    @abstractmethod
    async def automatic_scan_interval(self) -> int:
        """Returns the current automatic scan interval from the settings"""
        pass
    @property
    @abstractmethod
    async def aneurysm_high_risk_threshold(self) -> float:
        """Returns the current high risk threshold for aneurysm detection from the settings"""
        pass
    @property
    @abstractmethod
    async def aneurysm_medium_risk_threshold(self) -> float:
        """Returns the current medium risk threshold for aneurysm detection from the settings"""
        pass