from abc import ABC, abstractmethod

from app.core.patient_management.entities import AneurysmAnalysisResult


class ScanAnalyzer(ABC):
    @abstractmethod
    async def analyze_scan(
        self,
        scan_id: str,
        binary_data: bytes,
        explain: bool = False,
        target_label: str = "Aneurysm Present", 
    ) -> AneurysmAnalysisResult:
        """
        Analyze medical scans and returns Domain expected result entity
        along with explainability if present

        Args:
            scan_id: Unique identifier for the scan.
            binary_data: Raw DICOM file bytes.
            explain: If True, request Grad-CAM heatmaps from the AI.
            target_label: Which specific label to generate heatmaps for.
        """
        pass

class Notifier(ABC):
    @abstractmethod
    async def send_urgent_alert(self, scan_id: str, probability: float) -> bool:
        """Dispatches an urgent priority alert without exposing HIPAA/PHI data."""
        pass