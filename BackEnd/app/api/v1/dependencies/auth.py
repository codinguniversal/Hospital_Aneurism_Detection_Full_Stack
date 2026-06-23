from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import jwt
from app.infrastructure.security.jwt_provider import JWTTokenManager

# Authentication protocol scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Instantiate the token manager
token_manager = JWTTokenManager()


async def get_current_user_claims(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extracts, verifies, and returns the claims payload from the incoming JWT token.
    """
    try:
        return token_manager.decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token structure is corrupted.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RoleChecker:
    """A parameterized dependency wrapper used to restrict endpoints to specific roles."""
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, claims: dict = Depends(get_current_user_claims)) -> dict:
        user_role = claims.get("role")
        if not user_role or user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role '{user_role or 'Unknown'}' has insufficient permissions."
            )
        return claims