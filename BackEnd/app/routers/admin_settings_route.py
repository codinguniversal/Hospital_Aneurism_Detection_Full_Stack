from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_settings_use_case, get_update_settings_use_case
from app.modules.system_settings.entities import SettingsEntity
from app.modules.system_settings.use_cases import GetSettingsUseCase, UpdateSettingsUseCase
from app.schemas.setting_schema import SettingsResponseSchema, SettingsUpdateRequestSchema

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])

@router.put("",response_model= SettingsResponseSchema, status_code= status.HTTP_200_OK)
async def update_settings(
    settings_update_request: SettingsUpdateRequestSchema,
    use_case: UpdateSettingsUseCase = Depends(get_update_settings_use_case)
):
    try:
        new_settings = SettingsEntity(**settings_update_request.model_dump())

        await use_case.execute(new_settings)

        return SettingsResponseSchema(**new_settings.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("", response_model=SettingsResponseSchema, status_code=status.HTTP_200_OK)
async def get_settings(
    use_case: GetSettingsUseCase = Depends(get_settings_use_case)
):
    settings = await use_case.execute()
    return SettingsResponseSchema(**settings.model_dump())
