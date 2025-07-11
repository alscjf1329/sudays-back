from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class MemberBase(BaseModel):
    email: EmailStr
    nickname: str

class MemberCreate(BaseModel):
    email: str
    password: str
    nickname: str

class MemberResponse(BaseModel):
    id: str
    email: str
    nickname: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MemberInfoDTO(BaseModel):
    id: str
    email: str
    nickname: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmailPasswordRequestForm(BaseModel):
    email: str
    password: str 