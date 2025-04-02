from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, UUID, ARRAY
from datetime import datetime, UTC
from pydantic import BaseModel

Base = declarative_base()

class Diary(Base):
    __tablename__ = "diary"
    
    id = Column(UUID, primary_key=True)
    yyyymmdd = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    image_urls = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class DiarySaveDTO(BaseModel):
    yyyymmdd: str
    content: str
    image_urls: list[str] | None = None