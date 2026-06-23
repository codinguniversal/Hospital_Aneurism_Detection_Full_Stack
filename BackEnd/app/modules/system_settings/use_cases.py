from app.modules.system_settings.entities import SettingsEntity
from app.modules.system_settings.repositories import SettingsRepository


class GetSettingsUseCase:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo

    async def execute(self) -> SettingsEntity:
        return await self.settings_repo.get_settings()


class UpdateSettingsUseCase:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo

    async def execute(self, new_settings: SettingsEntity) -> None:
        await self.settings_repo.update_settings(new_settings)
