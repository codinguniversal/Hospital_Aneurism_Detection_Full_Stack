from app.domain.entities import SettingsEntity
from app.domain.repositories import SettingsRepository

class UpdateSettingsUseCase:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo

    async def execute(self, new_settings: SettingsEntity) -> None:
        await self.settings_repo.update_settings(new_settings)