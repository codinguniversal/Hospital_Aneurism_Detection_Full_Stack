from app.domain.repositories import UserRepository


class CheckEmailUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, email: str) -> bool:
        user = await self.user_repo.get_by_email(email)
        return user is not None
