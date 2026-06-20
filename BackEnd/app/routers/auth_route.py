from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.auth_schema import LoginRequestSchema, UserResponseSchema, RegisterRequestSchema

from app.usecases.auth_use_cases.auth_user_use_case import AuthenticateUserUseCase
from app.usecases.auth_use_cases.register_user_use_case import RegisterUserUseCase

from app.dependencies import get_authenticate_user_use_case, get_register_user_use_case

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login" ,response_model= UserResponseSchema, status_code= status.HTTP_200_OK)
async def login(
    login_request: LoginRequestSchema,
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

@router.post("/register", response_model= UserResponseSchema,status_code= status.HTTP_201_CREATED)
async def Register(
    register_request : RegisterRequestSchema,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    try:
        return await use_case.execute(register_request)
    except ValueError as e:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=str(e))
