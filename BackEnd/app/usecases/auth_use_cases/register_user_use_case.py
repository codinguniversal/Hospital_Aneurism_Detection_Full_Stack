from app.domain.services import IdGenerator
from app.domain.repositories import UserRepository
from app.domain.entities import UserEntity
from app.services.security import get_password_hash

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository, id_service: IdGenerator):
        self.user_repo = user_repo
        self.id_service = id_service

    async def execute(self, email: str, password: str) -> UserEntity:
        """
        Executes business rules for registration. 
        Completely isolated from HTTP schemas and data layer frameworks.
        """
        # Business Rule: Check for duplicates across unique identities
        if await self.user_repo.get_by_email(email):
            raise ValueError(f"A user with email '{email}' already exists.")
            
        new_id = await self.id_service.generate_6_digit_id()

        # Business Rule: Secure credentials
        hashed_pwd = get_password_hash(password)

        new_user = UserEntity(
            employee_id=new_id,
            email=email,
            password=hashed_pwd,
            role="Radiologist" 
        )

        await self.user_repo.add_user(new_user)
        return new_user