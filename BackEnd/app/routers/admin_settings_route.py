from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_update_settings_use_case
from app.domain.entities import SettingsEntity
from app.usecases.settings_use_cases.update_setings_use_case import UpdateSettingsUseCase
from app.schemas.setting_schema import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])

@router.put("",response_model= SettingsResponse, status_code= status.HTTP_200_OK)
async def update_settings(
    settings_update_request: SettingsUpdateRequest,
    use_case: UpdateSettingsUseCase = Depends(get_update_settings_use_case)
):
    try:
        new_settings = SettingsEntity(**settings_update_request.model_dump())

        await use_case.execute(new_settings)

        return SettingsResponse(**new_settings.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))