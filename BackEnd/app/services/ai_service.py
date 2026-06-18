import httpx
from pydantic import BaseModel
from app.domain.entities import AneurysmAnalysisResult, OverAllAneurysmPrediction, LocationPredictions
from app.config import settings

class AIResponseDTO(BaseModel):
    status: str
    overall_prediction: dict[str, float]
    detailed_locations: dict[str, float]

class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code

class AIService:
    def __init__(
            self,
            client: httpx.AsyncClient,
            base_url : str = settings.ai_api_url,
            timeout: int = settings.ai_timeout_limit
        ):
        self.client = client
        self.base_url = base_url
        self.timeout = timeout

    async def request_scan_analysis(
            self,
            scan_id: str,
            binary_data: bytes
        ) -> AneurysmAnalysisResult :
        files = {"file": (f"{scan_id}.zip", binary_data, "application/zip")}
        try:
            target_url = "http://127.0.0.1:8001/predict"
            
            print(f"\n[CROSS-SERVER COMMUNICATION] Routing from Backend (8000) -> AI Service (8001) via URL: {target_url}\n")
            response = await self.client.post(
                target_url,  # <-- Target the explicit route here
                files=files,
                timeout=self.timeout
            )
            
            # Catch 404 or 500 errors before attempting to parse JSON fields
            if response.status_code != 200:
                raise AIServiceError(
                    message=f"AI engine returned error status {response.status_code}: {response.text}",
                    status_code=502,
                )
                
            dto = AIResponseDTO.model_validate(response.json())
            
            if dto.status != "success":
                raise AIServiceError(
                    message="AI engine processed data but status returned unsuccessful.",
                    status_code=502,
                )
                
            return AneurysmAnalysisResult(
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
                )
            )
        
        except httpx.TimeoutException:
            raise AIServiceError(
                message="The external AI service took too long to respond.",
                status_code=504
            )
        except httpx.RequestError as exc:
            raise AIServiceError(
                message=f"Failed to communicate with external AI network: {exc}",
                status_code=503 
            )

_client = httpx.AsyncClient()
def get_ai_service() -> AIService:
    return AIService(client=_client)