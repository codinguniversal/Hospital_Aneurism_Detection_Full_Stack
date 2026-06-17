from typing import Optional

from app.domain.entities import UserEntity
from app.domain.repositories import UserRepository
from BackEnd.app.services.mock_data_layer import NoSQLDataLayer


class MockUserRepository(UserRepository):
    def __init__(self, data_layer: NoSQLDataLayer):
        self.data_layer = data_layer

    async def get_by_identifer(self, identifier: str) -> Optional[UserEntity]:
        raw_user = await self.data_layer.get_user_credentials(identifier, is_admin=False)
        if not raw_user:
            return None
        # MUST MATCH UserEntity
        return UserEntity(
            employee_id=raw_user["employeeId"],
            email=raw_user["email"],
            password=raw_user["password"],
            role=raw_user["role"]
        )