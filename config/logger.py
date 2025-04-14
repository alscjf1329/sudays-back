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

    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 로거 생성
    logger = logging.getLogger(name)
    
    if logger.handlers:
        _logger_cache[name] = logger
        return logger

    # 로그 레벨 설정
    log_level_str = os.getenv("LOG_LEVEL", "DEBUG").upper()  # 기본값을 DEBUG로 변경
    log_level = getattr(logging, log_level_str, logging.DEBUG)  # 기본값을 DEBUG로 변경
    logger.setLevel(log_level)

    # FastAPI 기본 로그 포맷
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, f"sudays.log"),
        when="midnight",
        interval=1,
        encoding="utf-8",
        backupCount=30,
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
    logger.propagate = True

    _logger_cache[name] = logger
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name is None:
        name = "root"
    return setup_logger(name)
