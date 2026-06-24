from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.dependencies.auth import RoleChecker, get_current_user_claims
from app.dependencies import build_update_settings_use_case, build_get_settings_use_case
from app.modules.system_settings.entities import SettingsEntity
from app.modules.system_settings.use_cases import GetSettingsUseCase, UpdateSettingsUseCase
from app.api.v1.schemas.setting_schema import SettingsResponseSchema, SettingsUpdateRequestSchema

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/settings", 
    tags=["Admin Settings"],
    dependencies=[Depends(RoleChecker(["Admin"]))] 
)

@router.put("",response_model= SettingsResponseSchema, status_code= status.HTTP_200_OK)
async def update_settings(
    settings_update_request: SettingsUpdateRequestSchema,
    use_case: UpdateSettingsUseCase = Depends(build_update_settings_use_case),
    current_user: dict = Depends(get_current_user_claims)
):
    """
    Update system settings. Only accessible by Admin users.
    Expects a SettingsUpdateRequestSchema in the request body.
    Returns the updated settings.
    """
    admin_id = current_user.get("sub","UNKNOWN")
    try:
        new_settings = SettingsEntity(**settings_update_request.model_dump())
        await use_case.execute(new_settings)
        
        logger.info(f"Admin {admin_id} Updated System Settings")
        return SettingsResponseSchema(**new_settings.model_dump())
    except ValueError as e:
        logger.error(f"Admin {admin_id} failed to update settings: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.critical(f"Unexpected error updating settings: {str(e)}", exc_info=True)
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.get("", response_model=SettingsResponseSchema, status_code=status.HTTP_200_OK)
async def get_settings(
    use_case: GetSettingsUseCase = Depends(build_get_settings_use_case),
    current_user: dict = Depends(get_current_user_claims)
):
    """
    Fetches the  system settings. Only accessible by Admin users.
    """
    try:
        settings = await use_case.execute()
        admin_id = current_user.get("sub", "UNKNOWN")
        logger.info(f"Admin {admin_id} retrieved system settings")
        return SettingsResponseSchema(**settings.model_dump())
    except Exception as e:
        logger.error(f"Failed to retrieve settings: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)