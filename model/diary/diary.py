from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, DateTime, UUID, ARRAY
from datetime import datetime, UTC
import uuid

Base = declarative_base()

class Diary(Base):
    __tablename__ = "diary"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    yyyymmdd = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    image_ids = Column(ARRAY(UUID), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))