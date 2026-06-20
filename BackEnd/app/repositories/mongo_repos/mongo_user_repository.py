from app.domain.entities import UserEntity
from app.domain.repositories import UserRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
class MongoUserRepository(UserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["Users"]
    
    async def get_by_identifier(self, identifier: str) -> UserEntity | None:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> UserEntity | None:
        raise NotImplementedError

    async def add_user(self, user: UserEntity) -> None:
        raise NotImplementedError
