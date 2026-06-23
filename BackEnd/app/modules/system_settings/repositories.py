from abc import ABC, abstractmethod

from app.modules.system_settings.entities import SettingsEntity


class SettingsRepository(ABC):
    @abstractmethod
    async def get_settings(self) -> SettingsEntity:
        """Fetches the current system settings (e.g., AI thresholds)"""
        pass

    @abstractmethod
    async def update_settings(self, settings: SettingsEntity) -> None:
        """Updates the system settings (e.g., AI thresholds)"""
        pass
