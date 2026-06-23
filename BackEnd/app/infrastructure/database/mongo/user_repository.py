from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.identity_access.entities import UserEntity
from app.modules.identity_access.repositories import UserRepository


class MongoUserRepository(UserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def get_by_identifier(self, employee_id: str) -> Optional[UserEntity]:
        raw_user = await self.collection.find_one({"employeeId": employee_id.strip()})

        if not raw_user:
            return None

        return UserEntity(
            employee_id=raw_user["employeeId"],
            email=raw_user["email"],
            password=raw_user["password"],
            role=raw_user["role"],
        )

    async def get_all_users(self) -> list:
        users_cursor = self.collection.find({})
        users_list = await users_cursor.to_list(length=100)

        return [UserEntity(**user) for user in users_list]

    async def get_by_employee_id(self, employee_id: str) -> Optional[UserEntity]:
        return await self.get_by_identifier(employee_id)

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        raw_user = await self.collection.find_one({"email": email.strip()})

        if not raw_user:
            return None

        return UserEntity(
            employee_id=raw_user["employeeId"],
            email=raw_user["email"],
            password=raw_user["password"],
            role=raw_user["role"],
        )

    async def add_user(self, user: UserEntity) -> None:
        user_document = {
            "employeeId": user.employee_id,
            "email": user.email,
            "password": user.password,
            "role": user.role,
        }

        await self.collection.update_one(
            {"email": user.email},
            {"$set": user_document},
            upsert=True,
        )

    async def delete_user_by_id(self, user_id: str) -> None:
        result = await self.collection.delete_one({"employeeId": user_id})

        if result.deleted_count == 0:
            raise ValueError(f"User with employee ID '{user_id}' not found")

        return None

    async def count_admins(self) -> int:
        return await self.collection.count_documents({"role": {"$regex": "^admin$", "$options": "i"}})
