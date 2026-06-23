from abc import ABC, abstractmethod

from app.core.patient_management.entities import AneurysmAnalysisResultEntity


class ScanAnalysisService(ABC):
    @abstractmethod
    async def analyze_scan(
        self,
        scan_id: str,
        binary_data: bytes,
    ) -> AneurysmAnalysisResultEntity:
        """Analyze medical scans and returns Domain expected result entity"""
        pass
