from sqlalchemy import Column, String, DateTime, Enum, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from model.base import Base

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