from sqlalchemy import Column, String, DateTime, Enum, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from config.database import Base

class MemberRole(enum.Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    USER = "USER"

class MemberGrade(enum.Enum):
    MEMBER = "MEMBER"
    NON_MEMBER = "NON_MEMBER"

class Member(Base):
    __tablename__ = 'member'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    role = Column(Enum(MemberRole), nullable=False, default=MemberRole.USER)
    grade = Column(Enum(MemberGrade), nullable=False, default=MemberGrade.NON_MEMBER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    diaries = relationship("Diary", back_populates="member")

    def __repr__(self):
        return f"<Member(id={self.id}, email={self.email}, nickname={self.nickname})>"

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        비밀번호가 다음 조건을 만족하는지 검증합니다:
        - 최소 8자 이상
        - 대문자, 소문자, 숫자, 특수문자 중 3가지 이상 포함
        """
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return sum([has_upper, has_lower, has_digit, has_special]) >= 3 