import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.diary.diary import router as diary_router
from controller.auth.auth_controller import router as auth_router
from controller.auth.verify_controller import router as verify_router
from config.database import init_database, create_tables
from config.logger import get_logger, setup_logger
import logging

# 환경 변수 먼저 로드
load_dotenv(os.getenv("ENV_FILE"))

# 로깅 설정 초기화
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)  # 로그 레벨을 명시적으로 설정

logger.info("╔════════════════════════════════════════════════════════╗")
logger.info("║                서버 시작 프로세스                      ║") 
logger.info("╠════════════════════════════════════════════════════════╣")

# 데이터베이스 초기화
init_database()
logger.info("║ ✅ 데이터베이스 초기화 완료")

# 서버 시작 시 테이블 생성
if os.getenv("DDL_AUTO") == "create":
    create_tables()
    logger.info("║ 📊 테이블 생성 완료")

## 환경 파일 검토
def check_env_file():
    logger.info("║ 🔍 환경 파일 검토 시작")
    if os.getenv("IMAGE_DIR") is None:
        logger.error("║ ❌ IMAGE_DIR 환경 변수가 설정되지 않았습니다")
        raise ValueError("IMAGE_DIR 환경 변수가 설정되지 않았습니다")
    logger.info("║ ✅ 환경 파일 검토 완료")

check_env_file()

app = FastAPI(
    title="Sudays API",
    description="Sudays 일기 서비스 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    # Postman 테스트를 위한 추가 설정
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"},
        {"url": "https://api.sudays.com", "description": "Production server"}
    ]
)

# Swagger UI에서 인증 설정
app.openapi = lambda: {
    "openapi": "3.0.0",
    "info": {
        "title": "Sudays API",
        "version": "1.0.0",
    },
    "components": {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "security": [{"Bearer": []}],
}

# CORS 미들웨어 설정
logger.info("║ 🔒 CORS 미들웨어 설정 시작")
origins = os.getenv("ALLOW_ORIGINS").split(",")
credentials = os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true"
methods = os.getenv("ALLOW_METHODS", "GET,POST,OPTIONS").split(",")
headers = os.getenv("ALLOW_HEADERS", "Content-Type,Authorization,authorization").split(",")

logger.info("║ 📝 CORS 설정 상세:")
logger.info(f"║   - Origins: {origins}")
logger.info(f"║   - Credentials: {credentials}")
logger.info(f"║   - Methods: {methods}")
logger.info(f"║   - Headers: {headers}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=credentials,
    allow_methods=methods,
    allow_headers=headers,
    expose_headers=["authorization"],
)
logger.info("║ ✅ CORS 미들웨어 설정 완료")

app.include_router(diary_router)
app.include_router(auth_router, tags=["auth"])
app.include_router(verify_router, prefix="/auth", tags=["auth"])
logger.info("║ 🚀 FastAPI 서버 시작 완료")
logger.info("╚════════════════════════════════════════════════════════╝")
