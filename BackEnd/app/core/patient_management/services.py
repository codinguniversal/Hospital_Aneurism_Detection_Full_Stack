from abc import ABC, abstractmethod

from app.core.patient_management.entities import AneurysmAnalysisResult


class ScanAnalyzer(ABC):
    @abstractmethod
    async def analyze_scan(
        self,
        scan_id: str,
        binary_data: bytes,
        explain: bool = True,
        target_label: str = "Aneurysm Present", 
    ) -> AneurysmAnalysisResult:
        """
        Analyze medical scans and returns Domain expected result entity
        along with explainability if present

        Args:
            scan_id: Unique identifier for the scan.
            binary_data: Raw DICOM file bytes.
            explain: Retained for service compatibility; Grad-CAM is always requested.
            target_label: Which specific label to generate heatmaps for.
        """
        pass

class Notifier(ABC):
    @abstractmethod
    async def send_urgent_alert(self, scan_id: str, probability: float) -> bool:
        """Dispatches an urgent priority alert without exposing HIPAA/PHI data."""
        pass
    def _format_alert_body(self, scan_id: str, probability: float) -> str:
        """
        Shared formatting logic for all notifiers.
        This ensures the message structure is identical in development and production.
        """
        return (
            f"URGENT CLINICAL ALERT\n\n"
            f"An automated backend scan analysis has completed with high-urgency metrics.\n"
            f"Scan Reference ID: {scan_id}\n"
            f"Highest Location Probability: {probability * 100:.1f}%\n\n"
            f"Please log into your hospital dashboard immediately."
        )