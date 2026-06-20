from pydantic import BaseModel, EmailStr

class LoginRequestSchema(BaseModel):
    loginIdentifier: str
    password: str
    isAdmin: bool
class UserResponseSchema(BaseModel):
    employee_id: str
    email:EmailStr
    role: str

class RegisterRequestSchema(BaseModel):
    username:str
    email: EmailStr
    password: str
    gender: str