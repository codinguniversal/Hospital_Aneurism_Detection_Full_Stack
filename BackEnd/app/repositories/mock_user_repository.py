from typing import Optional

from app.domain.entities import UserEntity
from app.domain.repositories import UserRepository
from app.services.mock_data_layer import MockNoSQLDataLayer


class MockUserRepository(UserRepository):
    def __init__(self, db: MockNoSQLDataLayer):
        self.db = db

    async def get_by_identifier(self, identifier: str) -> Optional[UserEntity]:
        raw_user = await self.db.get_user_credentials(identifier, is_admin=False)
        if not raw_user:
            return None
        # MUST MATCH UserEntity
        return UserEntity(
            employee_id=raw_user["employeeId"],
            email=raw_user["email"],
            password=raw_user["password"],
            role=raw_user["role"]
        )
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        raw_user = await self.db.get_user_credentials(email, is_admin=False)
        if not raw_user:
            return None
        return UserEntity(
            employee_id=raw_user["employeeId"],
            email=raw_user["email"],
            password=raw_user["password"],
            role=raw_user["role"]
        )
    async def add_user(self, user: UserEntity) -> None:
        self.db._users_collection[user.email] = {
            "employeeId": user.employee_id,
            "email": user.email,
            "password": user.password,
            "role": user.role
        }
        # print(self.data_layer._users_collection)