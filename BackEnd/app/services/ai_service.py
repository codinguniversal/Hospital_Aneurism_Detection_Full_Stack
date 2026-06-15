import httpx
from app.config import settings

class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code

class AIService:
    def __init__(self, client: httpx.AsyncClient, base_url : str = settings.ai_api_url, timeout: int = settings.ai_timeout_limit):
        self.client = client
        self.base_url = base_url
        self.timeout = timeout
    async def request_scan_analysis( self, scan_id: str, binary_data: bytes) -> dict :
        files = {"file": (f"{scan_id}.zip", binary_data, "application/zip")}
        try:
            response = await self.client.post(
                self.base_url,
                files=files,
                timeout= self.timeout
            )

            if response.status_code != 200:
                raise AIServiceError(
                    message = f"AI engine returned an unexpected error status: {response.status_code}",
                    status_code = 502,
                )
            return response.json()
        
        except httpx.TimeoutException:
            raise AIServiceError(
                message= "The external AI service took too long to respond.",
                status_code= 504
            )
        except httpx.RequestError as exc:
            raise AIServiceError(
                message = f"Failed to communicate with external AI network: {exc}",
                status_code= 503 
            )
_client = httpx.AsyncClient()
def get_ai_service() -> AIService:
    return AIService(client= _client)