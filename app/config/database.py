from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """데이터베이스 초기화"""
    pass

def create_tables():
    """테이블 생성"""
    # 모든 모델을 import하여 테이블 생성
    from model.member.member import Member
    from model.member.email_verification import EmailVerification
    from model.diary.diary import Diary
    from model.diary.diary_image import DiaryImage
    
    Base.metadata.create_all(bind=engine)