from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class CreateMemberRequestDTO(BaseModel):
    email: EmailStr
    nickname: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8)

class CreateMemberResponseDTO(BaseModel):
    id: str
    role: str
    email: EmailStr
    nickname: str = Field(..., min_length=2, max_length=50)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UpdateMemberRequestDTO(BaseModel):
    nickname: Optional[str] = Field(None, min_length=2, max_length=50)
    password: Optional[str] = Field(None, min_length=8)

class LoginMemberRequestDTO(BaseModel):
    email: EmailStr
    password: str