from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base 
from datetime import datetime, UTC
import uuid

Base = declarative_base()

class DiaryImage(Base):
    __tablename__ = "diary_image"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    file_name = Column(String(255), nullable=False)
    extension = Column(String(255), nullable=False)
    base_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))