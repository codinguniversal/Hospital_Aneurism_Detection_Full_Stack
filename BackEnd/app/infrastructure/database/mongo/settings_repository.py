from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import HttpUrl

from app.modules.system_settings.entities import SettingsEntity
from app.modules.system_settings.repositories import SettingsRepository


class MongoSettingsRepository(SettingsRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["Settings"]
        self._cached_settings: Optional[SettingsEntity] = None

    async def get_settings(self) -> SettingsEntity:
        if self._cached_settings is not None:
            return self._cached_settings

        raw_settings = await self.collection.find_one({"_id": "global_config"})

        if not raw_settings:
            fallback_settings = SettingsEntity(
                ai_api_url=HttpUrl("http://127.0.0.1:8001/predict"),
                ai_timeout_limit=12,
                automatic_scan_start_hour=1,
                automatic_scan_end_hour=2,
                automatic_scan_interval=1,
                aneurysm_high_risk_threshold=0.3,
                aneurysm_medium_risk_threshold=0.2,
            )
            await self.update_settings(fallback_settings)
            return fallback_settings

        self._cached_settings = SettingsEntity(**raw_settings["data"])
        return self._cached_settings

    async def update_settings(self, settings: SettingsEntity) -> None:
        document = {
            "_id": "global_config",
            "data": settings.model_dump(mode="json"),
        }

        await self.collection.update_one(
            {"_id": "global_config"},
            {"$set": document},
            upsert=True,
        )

        self._cached_settings = settings
