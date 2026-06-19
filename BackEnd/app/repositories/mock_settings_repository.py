from app.services.mock_data_layer import MockNoSQLDataLayer
from app.domain.entities import SettingsEntity
from app.domain.repositories import SettingsRepository

class MockSettingsRepository(SettingsRepository):
    def __init__(self, db=MockNoSQLDataLayer()):
        self.db = db
        self._cached_settings = None

    # --- Implement Required Abstract Properties ---

    @property
    def ai_api_url(self) -> str:
        return self._cached_settings.ai_api_url if self._cached_settings else "http://localhost:5000/predict"

    @property
    def ai_timeout_limit(self) -> int:
        return self._cached_settings.ai_timeout_limit if self._cached_settings else 30

    @property
    def automatic_scan_start_hour(self) -> int:
        return self._cached_settings.automatic_scan_start_hour if self._cached_settings else 1

    @property
    def automatic_scan_end_hour(self) -> int:
        return self._cached_settings.automatic_scan_end_hour if self._cached_settings else 5

    @property
    def automatic_scan_interval(self) -> int:
        return self._cached_settings.automatic_scan_interval if self._cached_settings else 60

    @property
    def aneurysm_high_risk_threshold(self) -> float:
        return self._cached_settings.aneurysm_high_risk_threshold if self._cached_settings else 0.8

    @property
    def aneurysm_medium_risk_threshold(self) -> float:
        return self._cached_settings.aneurysm_medium_risk_threshold if self._cached_settings else 0.5

    # --- Repository Methods ---

    async def get_settings(self) -> SettingsEntity:
        """
        Retrieves settings from the data layer. 
        Uses a local cache to avoid hitting the data layer on every call.
        """
        if self._cached_settings is None:
            raw_settings = None
            
            try:
                if hasattr(self.db, "find_one") or isinstance(self.db, dict):
                    raw_settings = self.db["_settings_collection"].get("current_config")
                else:
                    raw_settings = await self.db["_settings_collection"].find_one({"_id": "current_config"})
            except Exception:
                raw_settings = None

            if raw_settings is None:
                raw_settings = {
                    "ai_api_url": "http://localhost:5000/predict",
                    "ai_timeout_limit": 30,
                    "automatic_scan_start_hour": 1,
                    "automatic_scan_end_hour": 5,
                    "automatic_scan_interval": 60,
                    "aneurysm_high_risk_threshold": 0.8,
                    "aneurysm_medium_risk_threshold": 0.5
                }

            self._cached_settings = SettingsEntity(
                ai_api_url=raw_settings["ai_api_url"],
                ai_timeout_limit=raw_settings["ai_timeout_limit"],
                automatic_scan_start_hour=raw_settings["automatic_scan_start_hour"],
                automatic_scan_end_hour=raw_settings["automatic_scan_end_hour"],
                automatic_scan_interval=raw_settings["automatic_scan_interval"],
                aneurysm_high_risk_threshold=raw_settings["aneurysm_high_risk_threshold"],
                aneurysm_medium_risk_threshold=raw_settings["aneurysm_medium_risk_threshold"] 
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
            "aneurysm_medium_risk_threshold": new_settings.aneurysm_medium_risk_threshold
        }

        try:
            if hasattr(self.db, "replace_one"):
                await self.db["_settings_collection"].replace_one(
                    {"_id": "current_config"}, payload, upsert=True
                )
            else:
                self.db["_settings_collection"]["current_config"] = payload
        except Exception:
            pass

        self._cached_settings = new_settings