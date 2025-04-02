import os
from dotenv import load_dotenv
from fastapi import FastAPI
from controller.diary.diary import router as diary_router
from model.diary import Base
from config.database import init_database, init_db
from config.logger import get_logger

# 환경 변수 먼저 로드
load_dotenv(os.getenv("ENV_FILE"))

# 로거 설정
logger = get_logger()

logger.info(os.getenv("START_MESSAGE"))

# 데이터베이스 초기화
init_database()

# 서버 시작 시 테이블 생성
if os.getenv("DDL_AUTO") == "create":
    init_db()

## 환경 파일 검토
def check_env_file():
    logger.debug("환경 파일 검토를 시작합니다.")
    if os.getenv("IMAGE_DIR") is None:
        logger.error("IMAGE_DIR 환경 변수가 설정되지 않았습니다.")
        raise ValueError("IMAGE_DIR 환경 변수가 설정되지 않았습니다.")
    logger.info("환경 파일 검토가 완료되었습니다.")

check_env_file()

app = FastAPI()

## 라우터 등록
app.include_router(diary_router)