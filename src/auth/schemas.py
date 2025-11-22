from pydantic import BaseModel, ConfigDict, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str

class UserRead(BaseModel):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class AuthResponse(Token):
    user: UserRead
