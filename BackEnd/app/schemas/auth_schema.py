from pydantic import BaseModel, Emailstr

class LoginRequest(BaseModel):
    loginIdentifier: str
    password: str
    isAdmin: bool