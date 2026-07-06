from fastapi import APIRouter, HTTPException, status, Depends

from app.api.v1.dependencies.auth import get_token_manager
from app.modules.identity_access.use_cases import AuthenticateUserUseCase, RegisterUserUseCase
from app.api.v1.schemas.auth_schema import LoginRequestSchema, LoginResponseSchema, RegisterRequestSchema

from app.dependencies import build_authenticate_user_use_case, build_register_user_use_case

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login" ,response_model= LoginResponseSchema, status_code= status.HTTP_200_OK)
async def login(
    login_request: LoginRequestSchema,
    use_case: AuthenticateUserUseCase = Depends(build_authenticate_user_use_case),
):
    user = await use_case.execute(
        identifier= login_request.loginIdentifier,
        password= login_request.password,
    )
    print("\n" + "="*50)
    print("DEBUGGING AUTHENTICATION:")
    print(f"Incoming Login Identifier: '{login_request.loginIdentifier}'")
    print(f"Found User in DB?: {user is not None}")
    if user:
        print(f"DB Employee ID: '{user.employee_id}'")
        print(f"DB User Email:  '{user.email}'")
        print(f"DB User Role:   '{user.role}'")
    print("="*50 + "\n")

    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "invalid credentials or role selection"
        )

    token_manager = get_token_manager()
    token = token_manager.create_access_token(
        {
            "sub" : user.employee_id,
            "role" : user.role
        }
    )

    return LoginResponseSchema(
        employee_id= user.employee_id,
        email= user.email,
        role= user.role,
        access_token= token,
        token_type= "bearer"
    )

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequestSchema, 
    use_case: RegisterUserUseCase = Depends(build_register_user_use_case) 
):
    """Router layer: Manages the HTTP schema and maps values into the pure Use Case"""
    try:
        user_entity = await use_case.execute(
            email=request.email,
            password=request.password,
        )
        return {"status": "success", "user_id": user_entity.employee_id}
        
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))