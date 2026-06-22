from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.entities import UserEntity
from app.domain.repositories import UserRepository

class MongoUserRepository(UserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initializes the repository with a live Motor database instance.
        Targeting the 'users' collection.
        """
        self.collection = db["users"]

    async def get_by_identifier(self, employee_id: str) -> Optional[UserEntity]:
        """
        Finds a user if the identifier matches either their email, 
        their employeeId, or an explicit username field.
        """
        raw_user = await self.collection.find_one({"employeeId": employee_id.strip()})
        
        if not raw_user:
            return None
            
        return UserEntity(
            employee_id=raw_user["employeeId"],
            email=raw_user["email"],
            password=raw_user["password"],
            role=raw_user["role"]
        )

    async def get_all_users(self) -> list:
        """Retrieves all user documents from the MongoDB collection."""
        users_cursor = self._collection.find({})
        users_list = await users_cursor.to_list(length=100)
        
        # Map them back to your domain entities
        return [UserEntity(**user) for user in users_list]

    async def get_by_employee_id(self, employee_id: str) -> Optional[UserEntity]:
        """Looks up a user strictly by their unique employeeId using identifier logic."""
        return await self.get_by_identifier(employee_id)
    
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Looks up a user strictly by their email string."""
        raw_user = await self.collection.find_one({"email": email.strip()})
        
        if not raw_user:
            return None
            
        return UserEntity(
            employee_id=raw_user["employeeId"],
            email=raw_user["email"],
            password=raw_user["password"],
            role=raw_user["role"]
        )

    async def add_user(self, user: UserEntity) -> None:
        """
        Persists a new user record into the live MongoDB collection.
        """
        user_document = {
            "employeeId": user.employee_id,
            "email": user.email,
            "password": user.password,
            "role": user.role
        }
        
        await self.collection.update_one(
            {"email": user.email},
            {"$set": user_document},
            upsert=True
        )
    async def count_admins(self) -> int:
        return await self.collection.count_documents({"role": "admin"})