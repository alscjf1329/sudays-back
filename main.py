import os
from dotenv import load_dotenv
from fastapi import FastAPI
from controller.diary.diary import router as diary_router
from model.diary import Base
from config.database import init_database, init_db
from config.logger import setup_logger

# 환경 변수 먼저 로드
load_dotenv(os.getenv("ENV_FILE"))

# 로거 설정
logger = setup_logger()

logger.debug("디버그 메시지")
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")
logger.critical("치명적 에러 메시지")

logger.info(f"ENV_FILE: {os.getenv('ENV_FILE')}")

# 데이터베이스 초기화
init_database()

# 서버 시작 시 테이블 생성
if os.getenv("DDL_AUTO") == "create":
    init_db()

app = FastAPI()

app.include_router(diary_router)

logger.info("FastAPI 서버가 시작되었습니다.")