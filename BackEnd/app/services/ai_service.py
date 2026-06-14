import httpx
from fastapi import HTTPException, status
from app.config import settings



class AIService:
    def __init__(self, base_url : str = settings.ai_api_url, timeout: int = settings.ai_timeout_limit):
        self.base_url = base_url
        self.timeout = timeout
    async def request_scan_analysis( self, scan_id: str, binary_data: bytes) -> dict :
        files = {"file": (f"{scan_id}.zip", binary_data, "application/zip")}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, files=files, timeout= self.timeout)
                
                if response.status_code != status.HTTP_200_OK:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"AI engine returned an unexpected error status: {response.status_code}"
                    )
                return response.json()

            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="The external AI service took too long to respond. Processing failed."
                )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to communicate with the external AI network: {exc}"
                )
def get_ai_service() -> AIService:
    return AIService()