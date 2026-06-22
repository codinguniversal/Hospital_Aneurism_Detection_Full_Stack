from typing import List

from fastapi import APIRouter, HTTPException, status, Depends

from app.usecases.user_use_cases.delete_user_use_case import DeleteUserByIdUseCase
from app.usecases.user_use_cases.get_all_users_use_case import GetAllUsersUseCase
from app.dependencies import build_delete_user_by_id_use_case, build_get_all_users_use_case
from app.schemas.user_schema import UserResponseSchema
from app.routers.mappers import user_entities_to_user_response

router = APIRouter(prefix="/users", tags=["User management"])

@router.get("", response_model=List[UserResponseSchema])
async def get_all_users(
    use_case: GetAllUsersUseCase = Depends(build_get_all_users_use_case)
):
    users = await use_case.execute()
    if not users:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="No Users were found")
    
    users_response = user_entities_to_user_response(users)

    return users_response

@router.delete("/{user_id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    use_case: DeleteUserByIdUseCase = Depends(build_delete_user_by_id_use_case)
):
    await use_case.execute(user_id)
    