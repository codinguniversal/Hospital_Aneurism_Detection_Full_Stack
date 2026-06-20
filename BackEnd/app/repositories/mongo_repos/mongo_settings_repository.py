from pydantic import HttpUrl

from app.domain.entities import SettingsEntity
from app.domain.repositories import SettingsRepository

from motor.motor_asyncio import AsyncIOMotorDatabase
class MongoSettingsRepository(SettingsRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["Settings"]
    

    async def get_settings(self) -> SettingsEntity:
        """Replace with actual implementation"""
        filler_settings = SettingsEntity(
            ai_api_url= HttpUrl("http://127.0.0.1:8001/predict"),
            ai_timeout_limit= 12,
            automatic_scan_start_hour= 1,
            automatic_scan_end_hour=2,
            automatic_scan_interval= 1,
            aneurysm_high_risk_threshold= 0.3,
            aneurysm_medium_risk_threshold= 0.2
            )
        return filler_settings
    async def update_settings(self, settings: SettingsEntity) -> None:
        """
        replace with actual implmentation
        """
        pass
