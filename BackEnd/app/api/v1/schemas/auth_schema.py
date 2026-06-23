from pydantic import BaseModel, EmailStr

class LoginRequestSchema(BaseModel):
    loginIdentifier: str
    password: str
    isAdmin: bool

class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str
    employee_id: str
    email:EmailStr
    role: str

class RegisterRequestSchema(BaseModel):
    email: EmailStr
    password: str
    gender: str

class EmailCheckResponseSchema(BaseModel):
    exists: bool