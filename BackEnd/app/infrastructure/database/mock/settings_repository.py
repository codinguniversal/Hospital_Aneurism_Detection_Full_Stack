from typing import Optional

from app.infrastructure.database.mock.data_layer import MockNoSQLDataLayer
from app.modules.system_settings.entities import SettingsEntity
from app.modules.system_settings.repositories import SettingsRepository

_DEFAULT_SETTINGS = {
    "ai_api_url": "http://localhost:5000/predict",
    "ai_timeout_limit": 30,
    "automatic_scan_start_hour": 1,
    "automatic_scan_end_hour": 5,
    "automatic_scan_interval": 60,
    "aneurysm_high_risk_threshold": 0.8,
    "aneurysm_medium_risk_threshold": 0.5,
}


class MockSettingsRepository(SettingsRepository):
    def __init__(self, db: MockNoSQLDataLayer):
        self.db = db
        self._cached_settings: Optional[SettingsEntity] = None

    async def get_settings(self) -> SettingsEntity:
        if self._cached_settings is not None:
            return self._cached_settings

        raw = self.db.settings.get("current_config")

        if raw is None:
            await self._save_defaults()
            raw = self.db.settings["current_config"]

        self._cached_settings = SettingsEntity(
            ai_api_url=raw["ai_api_url"],
            ai_timeout_limit=raw["ai_timeout_limit"],
            automatic_scan_start_hour=raw["automatic_scan_start_hour"],
            automatic_scan_end_hour=raw["automatic_scan_end_hour"],
            automatic_scan_interval=raw["automatic_scan_interval"],
            aneurysm_high_risk_threshold=raw["aneurysm_high_risk_threshold"],
            aneurysm_medium_risk_threshold=raw["aneurysm_medium_risk_threshold"],
        )

        return self._cached_settings

    async def update_settings(self, new_settings: SettingsEntity) -> None:
        payload = {
            "ai_api_url": new_settings.ai_api_url,
            "ai_timeout_limit": new_settings.ai_timeout_limit,
            "automatic_scan_start_hour": new_settings.automatic_scan_start_hour,
            "automatic_scan_end_hour": new_settings.automatic_scan_end_hour,
            "automatic_scan_interval": new_settings.automatic_scan_interval,
            "aneurysm_high_risk_threshold": new_settings.aneurysm_high_risk_threshold,
            "aneurysm_medium_risk_threshold": new_settings.aneurysm_medium_risk_threshold,
        }

        self.db.settings["current_config"] = payload
        self._cached_settings = new_settings

    async def _save_defaults(self) -> None:
        self.db.settings["current_config"] = _DEFAULT_SETTINGS.copy()
