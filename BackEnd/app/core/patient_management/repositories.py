from abc import ABC, abstractmethod
from typing import List, Optional

from app.core.patient_management.entities import (
    AneurysmAnalysisResult,
    Patient,
    Scan,
)

class Patients(ABC):
    @abstractmethod
    async def get_all(self) -> List[Patient]:
        """Returns all patients in the hospital system (including pre-existing scans)"""
        pass

    @abstractmethod
    async def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Fetch details of a specific patient along with their pre-existing scans"""
        pass

    @abstractmethod
    async def get_scan_file(self, scan_id: str) -> Optional[bytes]:
        """Returns the raw binary bytes data of the scan file for a given scan_id."""
        pass

    @abstractmethod
    async def update_scan_results(self, scan_id: str, ai_results: AneurysmAnalysisResult) -> bool:
        """Atomically updates the pre-existing scan state and diagnostic probability values"""
        pass

    @abstractmethod
    async def get_all_pending_scans(self) -> List[Scan]:
        """retrieves all scans that have not been analyzed yet"""
        pass

    @abstractmethod
    async def store_slice_image(
        self,
        scan_id: str,
        slice_index: int,
        base64_data: str,
        image_kind: str = "overlay",
    ) -> str:
        """
        Persists one slice image and returns its reference for later access.
        """
        pass

    @abstractmethod
    async def get_slice_image(self, slice_ref:str)->Optional[bytes]:
        """
        Retrieves the raw binary image data given its reference.
        Returns None if the reference does not exist.
        """
        pass
