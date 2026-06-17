from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    loginIdentifier: str
    password: str
    isAdmin: bool
class RegisterRequest(BaseModel):
    username:str
    email: EmailStr
    password: str
    gender: str