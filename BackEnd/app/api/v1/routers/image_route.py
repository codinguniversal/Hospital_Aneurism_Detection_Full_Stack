from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from app.api.v1.dependencies.auth import RoleChecker, get_current_user_claims 
from app.core.patient_management.use_cases import GetSliceImage
from app.dependencies import build_get_slice_image_use_case


router = APIRouter(prefix="/api/v1/images", tags=["Images"])

def image_response_or_404(image_bytes: bytes | None) -> Response:
    if not image_bytes:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=image_bytes, media_type="image/png")


@router.get("")
async def get_slice_image_by_query(
    image_ref: str,
    token: str | None = Query(None, description="Auth token parameter for browser HTML img tags"),
    get_slice_image_use_case: GetSliceImage = Depends(build_get_slice_image_use_case),
):
    """Query form safely supports absolute Windows paths containing ':' and '\\'."""
    

    claims = None
    
    if token:
        try:
            pass
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid url parameters session token.")
    else:
        # Standard fallback: No query token found
        try:
            pass
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication credentials missing.")

  
    allowed_roles = ["radiologist", "doctor"]
    
    if claims:
        user_role = claims.get("role", "").lower()
        if user_role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role unauthorized.")

    image_bytes = await get_slice_image_use_case.execute(image_ref=image_ref)
    return image_response_or_404(image_bytes)