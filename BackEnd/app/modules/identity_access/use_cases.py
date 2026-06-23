from typing import List, Optional

from app.modules.identity_access.entities import UserEntity
from app.modules.identity_access.repositories import UserRepository
from app.modules.identity_access.services import IdGenerator
from BackEnd.app.infrastructure.services.security import get_password_hash, verify_password


class AuthenticateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, identifier: str, password: str) -> Optional[UserEntity]:
        clean_identifer = identifier.strip()
        user = await self.user_repo.get_by_identifier(clean_identifer)

        if not user:
            return None

        if not verify_password(password, user.password):
            return None

        return user


class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository, id_service: IdGenerator):
        self.user_repo = user_repo
        self.id_service = id_service

    async def execute(self, email: str, password: str) -> UserEntity:
        if await self.user_repo.get_by_email(email):
            raise ValueError(f"A user with email '{email}' already exists.")

        new_id = await self.id_service.generate_6_digit_id()
        hashed_pwd = get_password_hash(password)

        new_user = UserEntity(
            employee_id=new_id,
            email=email,
            password=hashed_pwd,
            role="Radiologist",
        )

        await self.user_repo.add_user(new_user)
        return new_user


class CheckEmailUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, email: str) -> bool:
        user = await self.user_repo.get_by_email(email)
        return user is not None


class GetAllUsersUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self) -> List[UserEntity]:
        users = await self.user_repo.get_all_users()
        return users


class DeleteUserByIdUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, user_id: str):
        user = await self.user_repo.get_by_identifier(user_id)

        if not user:
            raise ValueError(f"user with ID {user_id} not found")

        if user.role.lower() == "admin":
            admin_count = await self.user_repo.count_admins()
            if admin_count <= 1:
                raise PermissionError("Cannot delete the only system admin")

        await self.user_repo.delete_user_by_id(user_id=user_id)
