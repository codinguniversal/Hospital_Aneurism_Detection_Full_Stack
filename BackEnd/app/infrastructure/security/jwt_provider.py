import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config import static_settings

from app.modules.identity_access.services import TokenManager

class TokenExpiredError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

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
            expire = datetime.now(timezone.utc) + timedelta(hours=static_settings.ACCESS_TOKEN_EXPIRE_HOURS)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, static_settings.JWT_SECRET, algorithm=static_settings.JWT_ALGORITHM)
        return encoded_jwt


    def decode_access_token(self, token: str) -> dict:
        
        """
        Decodes an incoming JWT token string and returns its raw claims dictionary.
        Raises custom exceptions (TokenExpiredError or InvalidTokenError) 
        if the token is invalid or expired.
        Notice: We do NOT throw FastAPI HTTPExceptions here, keeping this file pure Python.
        """

        try:
            return jwt.decode(token, static_settings.JWT_SECRET, algorithms=[static_settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token Signature expired")
        except jwt.PyJWTError as e:
            raise InvalidTokenError(f"Invalid Token error: {str(e)}")
