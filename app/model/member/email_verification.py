from sqlalchemy import Column, String, DateTime, Boolean, UUID, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta
from config.database import Base

class EmailVerification(Base):
    __tablename__ = 'email_verification'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, index=True)
    verification_code = Column(String(6), nullable=False)  # 6자리 인증코드
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<EmailVerification(id={self.id}, email={self.email}, is_verified={self.is_verified})>"

    @property
    def is_expired(self) -> bool:
        """인증코드가 만료되었는지 확인"""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """인증코드가 유효한지 확인 (만료되지 않았고 아직 인증되지 않음)"""
        return not self.is_expired and not self.is_verified 