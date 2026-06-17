from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth_schema import LoginRequest, RegisterRequest

from app.usecases.auth_user_use_case import AuthenticateUserUseCase
from app.usecases.register_user_use_case import RegisterUserUseCase

from app.dependencies import get_authenticate_user_use_case, get_register_user_use_case

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

@router.post("/register", status_code= status.HTTP_201_CREATED)
async def Register(
    register_request : RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    try:
        return await use_case.execute(register_request)
    except ValueError as e:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=str(e))
