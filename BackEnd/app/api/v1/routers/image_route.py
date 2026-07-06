from fastapi import APIRouter, Depends,HTTPException
from fastapi.responses import Response
from app.api.v1.dependencies.auth import RoleChecker
from app.core.patient_management.repositories import Patients
from app.core.patient_management.use_cases import GetSliceImage
from app.dependencies import build_get_slice_image_use_case, build_patient_repository

router = APIRouter(prefix="/api/v1/images", tags=["Images"])

def image_response_or_404(image_bytes: bytes | None) -> Response:
    if not image_bytes:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=image_bytes, media_type="image/png")


@router.get(
        "")
async def get_slice_image_by_query(
    image_ref: str,
    get_slice_image_use_case: GetSliceImage = Depends(build_get_slice_image_use_case),
):
    """Query form safely supports absolute Windows paths containing ':' and '\\'."""
    image_bytes = await get_slice_image_use_case.execute(image_ref=image_ref)
    return image_response_or_404(image_bytes)


