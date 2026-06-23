from abc import ABC, abstractmethod
from typing import List, Optional

from app.modules.identity_access.entities import UserEntity


class UserRepository(ABC):
    @abstractmethod
    async def get_by_identifier(self, identifier: str) -> Optional[UserEntity]:
        """Fetch complete UserEntity by employee_id or return None"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Fetch details of a specific staff user based on their login email"""
        pass

    @abstractmethod
    async def add_user(self, user: UserEntity) -> None:
        """Persist a new user (admin/doctor) in the data layer"""
        pass

    @abstractmethod
    async def get_all_users(self) -> List[UserEntity]:
        """Fetches all users"""
        pass

    @abstractmethod
    async def delete_user_by_id(self, user_id: str):
        """deletes a user using their user id"""
        pass

    @abstractmethod
    async def count_admins(self) -> int:
        """Return the total number of users with role 'admin'."""
        pass
