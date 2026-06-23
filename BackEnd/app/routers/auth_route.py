from fastapi import APIRouter, HTTPException, status, Depends

from app.modules.identity_access.use_cases import AuthenticateUserUseCase, RegisterUserUseCase
from app.schemas.auth_schema import LoginRequestSchema, LoginResponseSchema, RegisterRequestSchema

from app.dependencies import get_authenticate_user_use_case, get_register_user_use_case

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login" ,response_model= LoginResponseSchema, status_code= status.HTTP_200_OK)
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

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequestSchema, 
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case) 
):
    """Router layer: Manages the HTTP schema and maps values into the pure Use Case"""
    try:
        # Pass fields matching your exact UseCase execute signature cleanly:
        user_entity = await use_case.execute(
            email=request.email,
            password=request.password
        )
        return {"status": "success", "user_id": user_entity.employee_id}
        
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))