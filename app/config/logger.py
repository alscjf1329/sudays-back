import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

# 전역 변수 대신 로거 인스턴스를 캐시하는 딕셔너리 사용
_logger_cache = {}

def setup_logger(name: str = "root") -> logging.Logger:
    # 이미 설정된 로거가 있으면 반환
    if name in _logger_cache:
        return _logger_cache[name]

    # 환경 변수에서 로그 설정 가져오기
    log_dir = os.getenv("LOG_DIR", "logs")
    app_log_file = os.getenv("APP_LOG_FILE", "sudays.log")
    log_level_str = os.getenv("LOG_LEVEL", "DEBUG").upper()
    log_level = getattr(logging, log_level_str, logging.DEBUG)
    
    # 로거 생성
    logger = logging.getLogger(name)
    
    if logger.handlers:
        _logger_cache[name] = logger
        return logger

    logger.setLevel(log_level)

    # FastAPI 기본 로그 포맷
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 로그 디렉토리 생성
    os.makedirs(log_dir, exist_ok=True)
    
    # File handler
    log_file = os.path.join(log_dir, app_log_file)
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding='utf-8',
        delay=False
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    file_handler.suffix = "%Y%m%d"

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    # 초기 로그 메시지로 설정 확인
    logger.info(f"로거 초기화 완료 - 이름: {name}, 레벨: {log_level_str}, 파일: {log_file}")

    _logger_cache[name] = logger
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name is None:
        name = "root"
    return setup_logger(name)
