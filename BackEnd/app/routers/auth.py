from fastapi import APIRouter, HTTPException, status, Depends
from app.usecases.auth_user_use_case import AuthenticateUserUseCase, get_authenticate_user_use_case
from app.schemas.auth_schema import LoginRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(
    login_request: LoginRequest,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case)
):
    user = await use_case.execute(
        identifier= login_request.loginIdentifier,
        password= login_request.password,
    )
    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "invalid credentials or role selection"
        )
    return user