from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm

class Token(BaseModel):
    access_token: str
    token_type: str

class MemberBase(BaseModel):
    email: EmailStr
    nickname: str

class MemberCreate(MemberBase):
    password: str

class Member(MemberBase):
    class Config:
        from_attributes = True

class EmailPasswordRequestForm(BaseModel):
    email: str
    password: str 