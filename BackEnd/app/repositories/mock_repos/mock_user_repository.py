from typing import List, Optional
from app.domain.entities import UserEntity
from app.domain.repositories import UserRepository
from app.services.mock_data_layer import MockNoSQLDataLayer

class MockUserRepository(UserRepository):
    def __init__(self, db: MockNoSQLDataLayer):
        self.db = db  

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        # Query the raw dictionary directly (just like collection.find_one)
        raw_user = self.db.users.get(email)
        if not raw_user:
            return None
        return UserEntity(
            employee_id=raw_user["employeeId"],
            email=raw_user["email"],
            password=raw_user["password"],
            role=raw_user["role"]
        )

    async def get_all_users(self) -> List[UserEntity]:
        # Query all raw users (just like collection.find({}))
        raw_users = list(self.db.users.values())
        return [
            UserEntity(
                employee_id=user["employeeId"],
                email=user["email"],
                password=user["password"],
                role=user["role"]
            )
            for user in raw_users
        ]

    async def add_user(self, user: UserEntity) -> None:
        # Direct dictionary insertion
        self.db.users[user.email] = {
            "employeeId": user.employee_id,
            "email": user.email,
            "password": user.password,
            "role": user.role
        }

    async def get_by_identifier(self, identifier: str) -> Optional[UserEntity]:
        """
        Finds a user by their employee ID (e.g.  '123456').
        """
        for raw_user in self.db.users.values():
            if raw_user["employeeId"] == identifier:
                return UserEntity(
                    employee_id=raw_user["employeeId"],
                    email=raw_user["email"],
                    password=raw_user["password"],
                    role=raw_user["role"]
                )
        return None
    
    async def count_admins(self) -> int:
        return sum(1 for user in self.db.users.values() if user.get("role", "").lower() == "admin")
    async def delete_user_by_id(self, user_id: str) -> None:
        """
        Delete a user by their Employee ID (e.g., 'USER-01' or 'ADMIN-01').
        Raises ValueError if the user is not found.
        """
        email_to_delete = None
        for email, user_data in self.db.users.items():
            if user_data.get("employeeId") == user_id:
                email_to_delete = email
                break

        if email_to_delete is None:
            raise ValueError(f"User with employee ID '{user_id}' not found")

        del self.db.users[email_to_delete]