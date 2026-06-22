from typing import Optional

from app.services.security import verify_password
from app.domain.repositories import UserRepository
from app.domain.entities import UserEntity

class AuthenticateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    async def execute(self, identifier: str, password: str) -> Optional[UserEntity]:
        """retrieves data from data_layer to verify user credentials"""
        
        clean_identifer = identifier.strip()

        user = await self.user_repo.get_by_identifier(clean_identifer)

        if not user:
            return None

        if not verify_password(password, user.password):
            return None
        
        return user
        
    


