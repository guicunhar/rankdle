from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: str | None = None  # merges guest history into the new account


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpgradeGuestRequest(BaseModel):
    device_id: str
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
