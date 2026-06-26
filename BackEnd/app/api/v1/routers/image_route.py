from fastapi import APIRouter, Depends,HTTPException
from fastapi.responses import Response
from app.core.patient_management.repositories import PatientRepository
from app.core.patient_management.use_cases import GetSliceImageUseCase
from app.dependencies import build_get_slice_image_use_case, build_patient_repository

router = APIRouter(prefix="/api/v1/images", tags=["Images"])

@router.get("/{image_ref:path}")
async def get_slice_image(
    image_ref: str,
    get_slice_image_use_case: GetSliceImageUseCase = Depends(build_get_slice_image_use_case)
):
    print("DEBUG: GETTING IMAGES")
    image_bytes = await get_slice_image_use_case.execute(image_ref= image_ref)
    if not image_bytes:
        print("DEBUG: NOT IMAGESFOUND")
        raise HTTPException(status_code=404, detail="Image not found")
    print("DEBUG: IMAGES FOUND")
    return Response(content=image_bytes, media_type="image/png")
