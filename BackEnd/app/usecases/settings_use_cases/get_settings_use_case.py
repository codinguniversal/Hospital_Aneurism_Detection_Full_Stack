from app.domain.entities import SettingsEntity
from app.domain.repositories import SettingsRepository

class GetSettingsUseCase:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings_repo = settings_repo

    async def execute(self) -> SettingsEntity:
        return await self.settings_repo.get_settings()