import httpx
from pydantic import BaseModel

from app.core.patient_management.entities import (
    AneurysmAnalysisResultEntity,
    LocationPredictionsEntity,
    OverAllAneurysmPredictionEntity,
)
from app.core.patient_management.services import ScanAnalysisService


class AIResponseDTO(BaseModel):
    status: str
    overall_prediction: dict[str, float]
    detailed_locations: dict[str, float]


class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


class HTTPXScanAnalysisService(ScanAnalysisService):
    def __init__(self, client: httpx.AsyncClient, base_url: str, timeout: int):
        self.client = client
        self.base_url = base_url
        self.timeout = timeout

    async def analyze_scan(self, scan_id: str, binary_data: bytes) -> AneurysmAnalysisResultEntity:
        files = {"file": (f"{scan_id}.zip", binary_data, "application/zip")}
        try:
            print(f"\n[CROSS-SERVER COMMUNICATION] Routing from Backend (8000) -> AI Service (8001) via URL: {self.base_url}\n")
            response = await self.client.post(
                self.base_url,
                files=files,
                timeout=self.timeout,
            )

            response.raise_for_status()

            dto = AIResponseDTO.model_validate(response.json())

            if dto.status != "success":
                raise AIServiceError(
                    message="AI engine processed data but status returned unsuccessful.",
                    status_code=502,
                )

            return self._map_to_entity(dto)

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

    def _map_to_entity(self, dto: AIResponseDTO) -> AneurysmAnalysisResultEntity:
        return AneurysmAnalysisResultEntity(
            overall=OverAllAneurysmPredictionEntity(
                probability=dto.overall_prediction["Aneurysm Present"]
            ),
            locations=LocationPredictionsEntity(
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
        )
