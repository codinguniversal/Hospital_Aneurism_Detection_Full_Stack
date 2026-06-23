from pydantic import BaseModel


class UserEntity(BaseModel):
    employee_id: str
    email: str
    password: str
    role: str
