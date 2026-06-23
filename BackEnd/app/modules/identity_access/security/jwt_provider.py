import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# security configurations
JWT_SECRET = "YOUR_SUPER_SECRET_ENVIRONMENT_KEY_2026"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

# authentication protocol scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Wraps a dictionary payload (e.g., identity metrics and roles), adds an 
    expiration window, and cryptographically signs it into a JWT string.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodes an incoming JWT token string and returns its raw claims dictionary.
    Raises standard PyJWT exceptions if the token is invalid or expired.
    Notice: We do NOT throw FastAPI HTTPExceptions here, keeping this file pure Python.
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])



def extract_and_verify_claims(token: str) -> dict:
    """
    Infrastructure handler that uses decode_access_token but safely 
    translates lower-level cryptographic errors into standard FastAPI HTTPExceptions.
    """
    try:
        return decode_access_token(token)
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


def enforce_role_whitelist(user_role: Optional[str], allowed_roles: list[str]) -> None:
    """
    Aborts route execution with a clear 403 Forbidden exception if the user's
    extracted role is missing or fails to match permitted authorization boundaries.
    """
    if not user_role or user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Role '{user_role or 'Unknown'}' has insufficient permissions."
        )