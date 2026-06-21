from abc import ABC, abstractmethod

from app.domain.entities import AneurysmAnalysisResultEntity

class ScanAnalysisService(ABC):
    @abstractmethod
    async def analyze_scan(
        self,
        scan_id: str,
        binary_data: bytes
    )->AneurysmAnalysisResultEntity:
        """Analyze medical scans and returns Domain expected result entity"""
        pass

class IdGenerator(ABC):
    @abstractmethod
    async def generate_6_digit_id(self)->str:
        """atomic generation of unique 6-digit ID."""
        pass