import base64
import io
import random
from typing import Any, Optional

from app.core.patient_management.entities import (
    AneurysmAnalysisResultEntity,
    LocationPredictionsEntity,
    OverAllAneurysmPredictionEntity,
    ExplainabilityEntity,
    TopSliceEntity,
)
from app.core.patient_management.services import ScanAnalysisService
from app.infrastructure.ai.ai_client import AIServiceError


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
        patient_repo: Optional[Any] = None,
        fixed_scan_id: Optional[str] = None,
    ):
        self.always_success = always_success
        self.fixed_overall_probability = fixed_overall_probability
        self.fixed_location_probabilities = fixed_location_probabilities or self._default_location_probs()
        self.simulate_timeout = simulate_timeout
        self.simulate_http_error = simulate_http_error
        self.simulate_status_failure = simulate_status_failure
        self.patient_repo = patient_repo
        self.fixed_scan_id = fixed_scan_id

    @staticmethod
    def _default_location_probs() -> dict[str, float]:
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
    def _generate_fake_raw_slice_base64(self, width: int = 512, height: int = 512) -> str:
        """Generate a fake grayscale raw slice PNG."""
        try:
            from PIL import Image
            # Create a gray gradient with a random circle to simulate anatomy
            img = Image.new("L", (width, height), color=128)
            # Just return a simple gradient for testing
            import numpy as np
            arr = np.random.randint(0, 255, (height, width), dtype=np.uint8)
            img = Image.fromarray(arr)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        except ImportError:
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    def _generate_fake_base64_png(self, width: int = 512, height: int = 512) -> str:
        """Generate a fake PNG in Base64."""
        try:
            from PIL import Image
            img = Image.new("RGB", (width, height), color=(255, 0, 0))
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        except ImportError:
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

    async def analyze_scan(
        self,
        scan_id: str,
        binary_data: bytes,
        explain: bool = False,  # ✅ Added to match abstract
        target_label: str = "Aneurysm Present",  # ✅ Added to match abstract
    ) -> AneurysmAnalysisResultEntity:
        # Simulate failures
        if self.simulate_timeout:
            raise AIServiceError("Mock AI timeout", status_code=504)
        if self.simulate_http_error:
            raise AIServiceError("Mock HTTP error", status_code=502)
        if self.simulate_status_failure:
            raise AIServiceError("Mock status failure (unsuccessful)", status_code=502)

        # Generate probabilities
        overall_prob = self.fixed_overall_probability
        if overall_prob is None:
            overall_prob = round(random.uniform(0.2, 0.95), 3)

        if self.fixed_location_probabilities:
            loc_probs = self.fixed_location_probabilities
        else:
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

        result = AneurysmAnalysisResultEntity(
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
            ),
            explainability=[],
        )

        # Mirror production behavior: explanations are always generated.
        if self.patient_repo:
            fake_slices = [
                {"slice_index": 42, "importance": 1.0},
                {"slice_index": 15, "importance": 0.85},
                {"slice_index": 71, "importance": 0.60},
            ]

            top_slices_entities = []
            for fake_slice in fake_slices:
                fake_overlay_base64 = self._generate_fake_base64_png()
                fake_raw_base64 = self._generate_fake_raw_slice_base64()
                fake_ref = await self.patient_repo.store_slice_image(
                    scan_id=scan_id,
                    slice_index=fake_slice["slice_index"],
                    base64_data=fake_overlay_base64,
                    image_kind="overlay",
                )
                raw_ref = await self.patient_repo.store_slice_image(
                    scan_id=scan_id,
                    slice_index=fake_slice["slice_index"],
                    base64_data=fake_raw_base64,
                    image_kind="raw",
                )

                top_slices_entities.append(
                    TopSliceEntity(
                        slice_index=fake_slice["slice_index"],
                        importance=fake_slice["importance"],
                        overlay_slice_image_ref=fake_ref,
                        raw_slice_image_ref= raw_ref
                    )
                )

            # ✅ Use the `target_label` passed from the Use Case
            explainability_entity = ExplainabilityEntity(
                id=f"exp_{scan_id}_{target_label.replace(' ', '_')}",
                method="Grad-CAM",
                target_label=target_label,  # ✅ Use the actual passed label
                top_slices=top_slices_entities,
                model_metadata={"mock": True, "simulated": True},
            )

            if result.explainability is None:
                result.explainability = []
            result.explainability.append(explainability_entity)

        return result
