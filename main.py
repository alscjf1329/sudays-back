import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.diary.diary import router as diary_router
from config.database import init_database, create_tables
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
    create_tables()

## 환경 파일 검토
def check_env_file():
    logger.debug("환경 파일 검토를 시작합니다.")
    if os.getenv("IMAGE_DIR") is None:
        logger.error("IMAGE_DIR 환경 변수가 설정되지 않았습니다.")
        raise ValueError("IMAGE_DIR 환경 변수가 설정되지 않았습니다.")
    logger.info("환경 파일 검토가 완료되었습니다.")

check_env_file()

app = FastAPI()

logger.info(os.getenv("ALLOW_ORIGINS").split(","))
logger.info(os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true")
logger.info(os.getenv("ALLOW_METHODS", "GET,POST,OPTIONS").split(","))
logger.info(os.getenv("ALLOW_HEADERS", "Content-Type,Authorization").split(","))

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOW_ORIGINS").split(","),
    allow_credentials=os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true",
    allow_methods=os.getenv("ALLOW_METHODS", "GET,POST,OPTIONS").split(","),
    allow_headers=os.getenv("ALLOW_HEADERS", "Content-Type,Authorization").split(","),
)

app.include_router(diary_router)
logger.info("FastAPI 서버가 시작되었습니다.")