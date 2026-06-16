from typing import Optional

from fastapi import Depends
from BackEnd.app.repositories.mock_user_repository import MockUserRepository
from BackEnd.app.services.data_layer import NoSQLDataLayer, get_data_layer
from app.domain.repositories import UserRepository
from app.domain.entities import UserEntity
class AuthenticateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    async def execute(self, identifier: str, password: str) -> Optional[UserEntity]:
        """retrieves data from data_layer to verify user credentials"""
        
        clean_identifer = identifier.strip()

        user = await self.user_repo.get_by_identifer(clean_identifer)

        if not user or user.password != password :
            return None
        
        return user

def get_user_repository(data_layer: NoSQLDataLayer = Depends(get_data_layer))-> UserRepository:
    return MockUserRepository(data_layer)
def get_authenticate_user_use_case(user_repo: UserRepository = Depends(get_user_repository)) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(user_repo=user_repo)
