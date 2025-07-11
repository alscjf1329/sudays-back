from sqlalchemy import Column, String, DateTime, UUID, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import uuid
from model.base import Base

class DiaryImage(Base):
    __tablename__ = "diary_image"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    diary_id = Column(UUID, ForeignKey('diary.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    extension = Column(String(255), nullable=False)
    base_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # 관계 설정
    diary = relationship("Diary", back_populates="images")