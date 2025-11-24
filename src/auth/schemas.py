from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr = Field(
        ...,
        title="Email address",
        description="User unique email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        title="Password",
        description="User password",
        min_length=8,
        examples=["password"]
    )

class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["password"])

class Token(BaseModel):
    access_token: str = Field(..., examples=['eyJhbGciOiJIUzI1NiIsInR5cC...'])
    token_type: str = Field(..., examples=['bearer'])

class UserRead(BaseModel):
    id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class AuthResponse(Token):
    user: UserRead
