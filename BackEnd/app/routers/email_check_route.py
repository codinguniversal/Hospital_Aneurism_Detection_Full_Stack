from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import EmailStr

from app.schemas.auth_schema import EmailCheckResponseSchema
from app.usecases.auth_use_cases.check_email_use_case import CheckEmailUseCase
from app.dependencies import get_check_email_use_case

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/check-email", response_model=EmailCheckResponseSchema, status_code=status.HTTP_200_OK)
async def check_email(
    email: EmailStr = Query(..., description="Email to check for existence"),
    use_case: CheckEmailUseCase = Depends(get_check_email_use_case)
):
    """
    Check if an email is already registered in the system.
    
    Returns:
    - exists: boolean indicating whether the email exists
    """
    try:
        email_exists = await use_case.execute(email=email)
        return EmailCheckResponseSchema(exists=email_exists)
    
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking email availability: {str(err)}"
        )
