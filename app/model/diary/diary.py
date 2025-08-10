from sqlalchemy import Column, String, Text, DateTime, UUID, ARRAY, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import uuid
from config.database import Base

class Diary(Base):
    __tablename__ = "diary"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    yyyymmdd = Column(String, nullable=False)
    member_id = Column(UUID, ForeignKey('member.id'), nullable=False)
    content = Column(Text, nullable=False)
    image_ids = Column(ARRAY(UUID), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    member = relationship("Member", back_populates="diaries")
    images = relationship("DiaryImage", back_populates="diary")
    
    __table_args__ = (
        UniqueConstraint('yyyymmdd', 'member_id', name='uix_diary_date_member'),
    )