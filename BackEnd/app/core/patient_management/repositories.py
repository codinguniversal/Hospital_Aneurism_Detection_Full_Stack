from abc import ABC, abstractmethod
from typing import List, Optional

from app.core.patient_management.entities import (
    AneurysmAnalysisResultEntity,
    PatientEntity,
    ScanEntity,
)


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
        """Returns the raw binary bytes data of the scan file for a given scan_id."""
        pass

    @abstractmethod
    async def update_scan_results(self, scan_id: str, ai_results: AneurysmAnalysisResultEntity) -> bool:
        """Atomically updates the pre-existing scan state and diagnostic probability values"""
        pass

    @abstractmethod
    async def get_all_pending_scans(self) -> List[ScanEntity]:
        """retrieves all scans that have not been analyzed yet"""
        pass
