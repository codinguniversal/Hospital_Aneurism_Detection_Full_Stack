from app.domain.repositories import UserRepository
from app.domain.entities import UserEntity
from app.services.security import get_password_hash

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, email: str, employee_id: str, password: str) -> UserEntity:
        """
        Executes business rules for registration. 
        Completely isolated from HTTP schemas and data layer frameworks.
        """
        # Business Rule: Check for duplicates across unique identities
        if await self.user_repo.get_by_email(email):
            raise ValueError(f"A user with email '{email}' already exists.")
            
        if await self.user_repo.get_by_employee_id(employee_id):
            raise ValueError(f"A user with employee ID '{employee_id}' already exists.")

        # Business Rule: Secure credentials
        hashed_pwd = get_password_hash(password)

        new_user = UserEntity(
            employee_id=employee_id,
            email=email,
            password=hashed_pwd,
            role="doctor"
        )

        await self.user_repo.add_user(new_user)
        return new_user