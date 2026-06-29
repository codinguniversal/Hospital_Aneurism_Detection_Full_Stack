from typing import List, Optional, Dict, Any

import httpx
from pydantic import BaseModel, ValidationError

from app.core.patient_management.repositories import Patients
from app.core.patient_management.entities import (
    AneurysmAnalysisResult,
    AnalysisRationale,
    LocationPredictions,
    OverAllAneurysmPrediction,
    TopSlice,
)
from app.core.patient_management.services import ScanAnalyzer

class TopSliceDTO(BaseModel):
    slice_index: int
    importance: float
    overlay_png_base64: str
    raw_slice_png_base64: Optional[str] = None

class ExplainabilityDTO(BaseModel):
    method: str
    target_label: str
    top_slices: List[TopSliceDTO]
    model_explanations: Optional[List[Dict[str,Any]]] = None

class AIResponseDTO(BaseModel):
    status: str
    overall_prediction: Dict[str, float]
    detailed_locations: Dict[str, float]
    # Normal predictions intentionally omit Grad-CAM data unless the caller
    # requests an explanation.
    explainability: Optional[ExplainabilityDTO] = None


class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


class HTTPXScanAnalysisService(ScanAnalyzer):
    def __init__(
            self,
            client: httpx.AsyncClient,
            base_url: str,
            patient_repo: Patients,
            timeout: int = 60,
        ):
        self.client = client
        self.base_url = base_url
        self.patient_repo = patient_repo
        self.timeout = timeout

    async def analyze_scan(
                self,
                scan_id: str,
                binary_data: bytes,
            explain: bool = True,
                target_label: str = "Aneurysm Present",
            ) -> AneurysmAnalysisResult:
        
        query_params = {
            "explain": "true",
            "target_label": target_label,
        }
        
        files = {"file": (f"{scan_id}.zip", binary_data, "application/zip")}
        try:
            print(f"\n[CROSS-SERVER] Backend -> AI Service: {self.base_url} with params {query_params}\n")
            response = await self.client.post(
                self.base_url,
                files=files,
                params= query_params,
                timeout=self.timeout,
            )
            response.raise_for_status()

            dto = AIResponseDTO.model_validate(response.json())

            if dto.status != "success":
                raise AIServiceError(
                    message="AI engine processed data but status returned unsuccessful.",
                    status_code=502,
                )

            return await self._map_to_entity(scan_id= scan_id, dto= dto)

        except httpx.HTTPStatusError as exc:
            raise AIServiceError(
                message=f"AIService HTTP Error {exc.response.status_code}: {exc.response.text}",
                status_code=502,
            )
        except httpx.TimeoutException:
            raise AIServiceError(
                message="The external AI service took too long to respond.",
                status_code=504,
            )
        except httpx.RequestError as exc:
            raise AIServiceError(
                message=f"Failed to communicate with external AI network: {exc}",
                status_code=503,
            )
        except (ValidationError, KeyError, TypeError) as exc:
            raise AIServiceError(
                message=f"AI service returned an invalid response payload: {exc}",
                status_code=502,
            ) from exc

    async def _map_to_entity(
            self,
            scan_id: str,
            dto: AIResponseDTO
        ) -> AneurysmAnalysisResult:
        result = AneurysmAnalysisResult(
            overall=OverAllAneurysmPrediction(
                probability=dto.overall_prediction["Aneurysm Present"]
            ),
            locations=LocationPredictions(
                LeftInfraclinoidInternalCarotidArtery=dto.detailed_locations["Left Infraclinoid Internal Carotid Artery"],
                RightInfraclinoidInternalCarotidArtery=dto.detailed_locations["Right Infraclinoid Internal Carotid Artery"],
                LeftSupraclinoidInternalCarotidArtery=dto.detailed_locations["Left Supraclinoid Internal Carotid Artery"],
                RightSupraclinoidInternalCarotidArtery=dto.detailed_locations["Right Supraclinoid Internal Carotid Artery"],
                LeftMiddleCerebralArtery=dto.detailed_locations["Left Middle Cerebral Artery"],
                RightMiddleCerebralArtery=dto.detailed_locations["Right Middle Cerebral Artery"],
                AnteriorCommunicatingArtery=dto.detailed_locations["Anterior Communicating Artery"],
                LeftAnteriorCerebralArtery=dto.detailed_locations["Left Anterior Cerebral Artery"],
                RightAnteriorCerebralArtery=dto.detailed_locations["Right Anterior Cerebral Artery"],
                LeftPosteriorCommunicatingArtery=dto.detailed_locations["Left Posterior Communicating Artery"],
                RightPosteriorCommunicatingArtery=dto.detailed_locations["Right Posterior Communicating Artery"],
                BasilarTip=dto.detailed_locations["Basilar Tip"],
                OtherPosteriorCirculation=dto.detailed_locations["Other Posterior Circulation"],
            ),
            explainability= []
        )
        if dto.explainability:
            top_slices_entities = []
            for slice_dto in dto.explainability.top_slices:
                overlay_ref = await self.patient_repo.store_slice_image(
                    scan_id= scan_id,
                    slice_index= slice_dto.slice_index,
                    base64_data= slice_dto.overlay_png_base64,
                    image_kind="overlay",
                )
                if slice_dto.raw_slice_png_base64:
                    raw_ref = await self.patient_repo.store_slice_image(
                        scan_id= scan_id,
                        slice_index=slice_dto.slice_index,
                        base64_data= slice_dto.raw_slice_png_base64,
                        image_kind="raw",
                    )
                else:
                    # placeholder
                    raw_ref = f"placeholder://scans/{scan_id}/slice_{slice_dto.slice_index}_raw.png"
                    print(f"WARNING: Raw slice not provided by AI for scan {scan_id}, slice {slice_dto.slice_index}")
                top_slices_entities.append(
                    TopSlice(
                        slice_index=slice_dto.slice_index,
                        importance=slice_dto.importance,
                        overlay_slice_image_ref= overlay_ref,
                        raw_slice_image_ref= raw_ref
                    )
                )
            explainability_entity = AnalysisRationale(
                id=f"exp_{scan_id}_{dto.explainability.target_label.replace(' ', '_')}",
                method=dto.explainability.method,
                target_label=dto.explainability.target_label,
                top_slices=top_slices_entities,
                model_metadata=dto.explainability.model_explanations,
            )
            if result.explainability is None:
                result.explainability = []
            result.explainability.append(explainability_entity)
        return result
        
