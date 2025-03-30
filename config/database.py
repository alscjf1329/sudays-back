from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from model.diary import Base

def get_database_url():
    return f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = None
SessionLocal = None

def init_database():
    global engine, SessionLocal
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    if engine is None:
        init_database()
    Base.metadata.create_all(bind=engine)

def get_db():
    if SessionLocal is None:
        init_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()