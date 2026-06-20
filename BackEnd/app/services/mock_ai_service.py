import random
from typing import Optional
from app.domain.entities import (
    AneurysmAnalysisResultEntity,
    OverAllAneurysmPredictionEntity,
    LocationPredictionsEntity
)
from app.domain.services import ScanAnalysisService
from app.services.ai_service import AIServiceError


class MockScanAnalysisService(ScanAnalysisService):
    """
    A fake implementation of ScanAnalysisService that returns predefined
    or random results without network calls. Useful for testing and development.
    """

    def __init__(
        self,
        always_success: bool = True,
        fixed_overall_probability: Optional[float] = None,
        fixed_location_probabilities: Optional[dict[str, float]] = None,
        simulate_timeout: bool = False,
        simulate_http_error: bool = False,
        simulate_status_failure: bool = False,
    ):
        """
        Args:
            always_success: If True, always return successful results.
            fixed_overall_probability: If set, use this value for overall prediction.
            fixed_location_probabilities: If set, use these values for location predictions.
            simulate_timeout: If True, raise AIServiceError with status 504.
            simulate_http_error: If True, raise AIServiceError with status 502.
            simulate_status_failure: If True, raise AIServiceError with message "unsuccessful status".
        """
        self.always_success = always_success
        self.fixed_overall_probability = fixed_overall_probability
        self.fixed_location_probabilities = fixed_location_probabilities or self._default_location_probs()
        self.simulate_timeout = simulate_timeout
        self.simulate_http_error = simulate_http_error
        self.simulate_status_failure = simulate_status_failure

    @staticmethod
    def _default_location_probs() -> dict[str, float]:
        """Return a dict of default location probabilities for a high-risk aneurysm."""
        return {
            "Left Infraclinoid Internal Carotid Artery": 0.85,
            "Right Infraclinoid Internal Carotid Artery": 0.10,
            "Left Supraclinoid Internal Carotid Artery": 0.05,
            "Right Supraclinoid Internal Carotid Artery": 0.02,
            "Left Middle Cerebral Artery": 0.95,
            "Right Middle Cerebral Artery": 0.15,
            "Anterior Communicating Artery": 0.60,
            "Left Anterior Cerebral Artery": 0.30,
            "Right Anterior Cerebral Artery": 0.20,
            "Left Posterior Communicating Artery": 0.40,
            "Right Posterior Communicating Artery": 0.25,
            "Basilar Tip": 0.55,
            "Other Posterior Circulation": 0.10,
        }

    async def analyze_scan(
        self, scan_id: str, binary_data: bytes
    ) -> AneurysmAnalysisResultEntity:
        """Simulate analyzing a scan. Returns fake results or raises errors as configured."""
        # Simulate errors first
        if self.simulate_timeout:
            raise AIServiceError("Mock AI timeout", status_code=504)
        if self.simulate_http_error:
            raise AIServiceError("Mock HTTP error", status_code=502)
        if self.simulate_status_failure:
            raise AIServiceError("Mock status failure (unsuccessful)", status_code=502)

        # Build the result
        overall_prob = self.fixed_overall_probability
        if overall_prob is None:
            # Random probability between 0.2 and 0.95
            overall_prob = round(random.uniform(0.2, 0.95), 3)

        # Use fixed location probabilities (or generate random ones if not set)
        if self.fixed_location_probabilities:
            loc_probs = self.fixed_location_probabilities
        else:
            # Generate random values for each location (between 0 and 1)
            loc_probs = {
                "Left Infraclinoid Internal Carotid Artery": round(random.random(), 3),
                "Right Infraclinoid Internal Carotid Artery": round(random.random(), 3),
                "Left Supraclinoid Internal Carotid Artery": round(random.random(), 3),
                "Right Supraclinoid Internal Carotid Artery": round(random.random(), 3),
                "Left Middle Cerebral Artery": round(random.random(), 3),
                "Right Middle Cerebral Artery": round(random.random(), 3),
                "Anterior Communicating Artery": round(random.random(), 3),
                "Left Anterior Cerebral Artery": round(random.random(), 3),
                "Right Anterior Cerebral Artery": round(random.random(), 3),
                "Left Posterior Communicating Artery": round(random.random(), 3),
                "Right Posterior Communicating Artery": round(random.random(), 3),
                "Basilar Tip": round(random.random(), 3),
                "Other Posterior Circulation": round(random.random(), 3),
            }

        # Build the entity
        return AneurysmAnalysisResultEntity(
            overall=OverAllAneurysmPredictionEntity(probability=overall_prob),
            locations=LocationPredictionsEntity(
                LeftInfraclinoidInternalCarotidArtery=loc_probs["Left Infraclinoid Internal Carotid Artery"],
                RightInfraclinoidInternalCarotidArtery=loc_probs["Right Infraclinoid Internal Carotid Artery"],
                LeftSupraclinoidInternalCarotidArtery=loc_probs["Left Supraclinoid Internal Carotid Artery"],
                RightSupraclinoidInternalCarotidArtery=loc_probs["Right Supraclinoid Internal Carotid Artery"],
                LeftMiddleCerebralArtery=loc_probs["Left Middle Cerebral Artery"],
                RightMiddleCerebralArtery=loc_probs["Right Middle Cerebral Artery"],
                AnteriorCommunicatingArtery=loc_probs["Anterior Communicating Artery"],
                LeftAnteriorCerebralArtery=loc_probs["Left Anterior Cerebral Artery"],
                RightAnteriorCerebralArtery=loc_probs["Right Anterior Cerebral Artery"],
                LeftPosteriorCommunicatingArtery=loc_probs["Left Posterior Communicating Artery"],
                RightPosteriorCommunicatingArtery=loc_probs["Right Posterior Communicating Artery"],
                BasilarTip=loc_probs["Basilar Tip"],
                OtherPosteriorCirculation=loc_probs["Other Posterior Circulation"],
            )
        )