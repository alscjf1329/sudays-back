import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logger():
    # 로그 디렉토리 생성
    log_dir = os.getenv("LOG_DIR", "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 로거 설정
    logger = logging.getLogger('sudays')
    
    # 환경 변수에 따른 로그 레벨 설정
    mode = os.environ.get('mode', 'prod')  # 기본값은 prod
    log_level = logging.DEBUG if mode == 'dev' else logging.INFO
    logger.setLevel(log_level)

    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 파일 핸들러 설정 (일별 로그 파일에 기록)
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'sudays.log'),
        when='midnight',  # 매일 자정에 새로운 파일 생성
        interval=1,  # 1일 간격
        encoding='utf-8',
        backupCount=30  # 30일치 로그 파일 보관
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y%m%d"  # 로그 파일명 형식 지정

    # 콘솔 핸들러 설정 (터미널에 출력)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger