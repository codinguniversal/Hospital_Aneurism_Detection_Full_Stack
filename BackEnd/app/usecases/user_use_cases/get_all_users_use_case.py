
from typing import List

from app.domain.entities import UserEntity
from app.domain.repositories import UserRepository


class GetAllUsersUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    async def execute(self)->List[UserEntity]:
        users = await self.user_repo.get_all_users()
        return users


