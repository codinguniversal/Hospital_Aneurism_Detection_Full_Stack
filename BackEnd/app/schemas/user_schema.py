from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    employee_id: str
    email: EmailStr
    password: str
    role: str

class UserResponseSchema(BaseModel):
    employee_id: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True