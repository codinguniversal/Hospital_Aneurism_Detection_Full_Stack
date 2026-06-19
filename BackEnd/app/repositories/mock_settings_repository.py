from app.services.mock_data_layer import MockNoSQLDataLayer
from app.domain.entities import SettingsEntity
from app.domain.repositories import SettingsRepository

class MockSettingsRepository(SettingsRepository):
    def __init__(self, db= MockNoSQLDataLayer()):
        self.db = db
        self._cached_settings = None

    async def get_settings(self) -> SettingsEntity:
        """
        Retrieves settings from the mock data layer. 
        Uses a local cache to avoid hitting the data layer on every call.
        """
        if self._cached_settings is None:
            raw_settings= self.db._settings_collection["current_config"]
            settings= SettingsEntity(
                ai_api_url=raw_settings["ai_api_url"],
                ai_timeout_limit=raw_settings["ai_timeout_limit"],
                automatic_scan_start_hour=raw_settings["automatic_scan_start_hour"],
                automatic_scan_end_hour=raw_settings["automatic_scan_end_hour"],
                automatic_scan_interval=raw_settings["automatic_scan_interval"],
                aneurysm_high_risk_threshold=raw_settings["aneurysm_high_risk_threshold"],
                aneurysm_medium_risk_threshold=raw_settings["aneurysm_medium_risk_threshold"] 
            )
            self._cached_settings = settings
        return self._cached_settings

    async def update_settings(self, new_settings: SettingsEntity) -> None:
        self.db._settings_collection["current_config"] = {
            "ai_api_url": new_settings.ai_api_url,
            "ai_timeout_limit": new_settings.ai_timeout_limit,
            "automatic_scan_start_hour": new_settings.automatic_scan_start_hour,
            "automatic_scan_end_hour": new_settings.automatic_scan_end_hour,
            "automatic_scan_interval": new_settings.automatic_scan_interval,
            "aneurysm_high_risk_threshold": new_settings.aneurysm_high_risk_threshold,
            "aneurysm_medium_risk_threshold": new_settings.aneurysm_medium_risk_threshold
        }
        self._cached_settings = new_settings