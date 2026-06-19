from app.domain.repositories import UserRepository
from app.domain.entities import UserEntity
from app.schemas.auth_schema import RegisterRequest

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    async def execute(self, request: RegisterRequest)-> UserEntity:
        existing_user = await self.user_repo.get_by_identifier(request.email) #this code needs to be cleaned up, we have email, emp id, and username.
        if existing_user:
            raise ValueError(f"User with identifier: {request.username} already exists in the data layer")
        new_user = UserEntity(
            employee_id= request.username,
            email= request.email,
            password= request.password,
            role= "doctor" #default as admin adds new doctors or radiologiest not other admins
        )
        await self.user_repo.add_user(new_user)
        return new_user