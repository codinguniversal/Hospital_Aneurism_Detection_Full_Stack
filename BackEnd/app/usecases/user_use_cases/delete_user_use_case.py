
from app.domain.repositories import UserRepository


class DeleteUserByIdUseCase:
    def __init__(self, user_repo: UserRepository)-> None:
        self.user_repo= user_repo
    async def execute(self, user_id: str):
        user = await self.user_repo.get_by_identifier(user_id)

        if not user:
            raise ValueError(f"user with ID {user_id} not found")
        
        if user.role.lower() == "admin":
            all_users = await self.user_repo.get_all_users()
            admin_count = await self.user_repo.count_admins()
            if admin_count <= 1:
                raise PermissionError("Cannot delete the only system admin")
            
        await self.user_repo.delete_user_by_id(user_id= user_id)