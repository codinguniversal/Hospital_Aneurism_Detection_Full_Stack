import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.modules.identity_access.services import TokenManager

# security configurations
JWT_SECRET = "YOUR_SUPER_SECRET_ENVIRONMENT_KEY_2026"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

# authentication protocol scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class JWTTokenManager(TokenManager):
    def create_access_token(self,data: dict, expires_delta: Optional[timedelta] = None) -> str:
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


    def decode_access_token(self, token: str) -> dict:
        """
        Decodes an incoming JWT token string and returns its raw claims dictionary.
        Raises standard PyJWT exceptions if the token is invalid or expired.
        Notice: We do NOT throw FastAPI HTTPExceptions here, keeping this file pure Python.
        """
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
