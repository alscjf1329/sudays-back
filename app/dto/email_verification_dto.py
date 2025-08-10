from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re
from config.email_config import EmailConfig

class SendVerificationCodeRequestDTO(BaseModel):
    email: EmailStr
    
    @validator('email')
    def validate_email_format(cls, v):
        if EmailConfig.ENABLE_EMAIL_VALIDATION:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError('올바른 이메일 형식이 아닙니다')
        return v.lower()  # 이메일을 소문자로 정규화

class SendVerificationCodeResponseDTO(BaseModel):
    message: str
    email: str
    expires_in_minutes: int = EmailConfig.VERIFICATION_CODE_EXPIRE_MINUTES

class VerifyCodeRequestDTO(BaseModel):
    email: EmailStr
    verification_code: str
    
    @validator('email')
    def validate_email_format(cls, v):
        if EmailConfig.ENABLE_EMAIL_VALIDATION:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError('올바른 이메일 형식이 아닙니다')
        return v.lower()
    
    @validator('verification_code')
    def validate_verification_code(cls, v):
        if not v.isdigit() or len(v) != EmailConfig.VERIFICATION_CODE_LENGTH:
            raise ValueError(f'인증코드는 {EmailConfig.VERIFICATION_CODE_LENGTH}자리 숫자여야 합니다')
        return v

class VerifyCodeResponseDTO(BaseModel):
    message: str
    is_verified: bool
    email: str
    verified_at: Optional[datetime] = None

class EmailVerificationDTO(BaseModel):
    id: str
    email: str
    is_verified: bool
    expires_at: datetime
    created_at: datetime
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True 