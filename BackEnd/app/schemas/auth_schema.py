from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    loginIdentifier: str
    password: str
    isAdmin: bool
class UserResponse(BaseModel):
    employee_id: str
    email:EmailStr
    role: str

class RegisterRequest(BaseModel):
    username:str
    email: EmailStr
    password: str
    gender: str