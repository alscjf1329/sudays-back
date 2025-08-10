#!/bin/bash

cd "$BIN_DIR"
source ./env.sh

cd "$APP_DIR"

# ========================= 서비스 상태 확인 ============================
echo "=========================================="
echo "서비스 상태"
echo "=========================================="

# Uvicorn 서버 상태 확인 (PID 파일 기반)
if [ -f "$PID_FILE" ]; then
    UVICORN_PID=$(cat "$PID_FILE")
    if kill -0 "$UVICORN_PID" 2>/dev/null; then
        echo "서버: 실행 중 (PID: $UVICORN_PID)"
        echo "포트: 사용 중"
    else
        echo "서버: 중지됨"
        rm -f "$PID_FILE"
    fi
else
    echo "서버: 중지됨"
fi

# Docker 컨테이너 상태 확인
if docker info > /dev/null 2>&1; then
    if docker ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
        echo "Docker: 실행 중"
    else
        echo "Docker: 중지됨"
    fi
else
    echo "Docker: 연결 안됨"
fi

# 데이터베이스 연결 상태 확인
if (echo > /dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT) 2>/dev/null || \
   (python3 -c "import socket; socket.socket().connect((\"$POSTGRES_HOST\", $POSTGRES_PORT))" 2>/dev/null); then
    echo "DB: 연결됨"
else
    echo "DB: 연결 안됨"
fi

# 로그 파일 상태 확인
echo "로그 파일:"
LOG_FILES=(
    "$LOG_DIR/uvicorn.log"
    "$LOG_DIR/access.log"
    "$LOG_DIR/error.log"
    "$PID_FILE"
)

for log_file in "${LOG_FILES[@]}"; do
    if [ -f "$log_file" ]; then
        if [ "$log_file" = "$PID_FILE" ]; then
            echo "  $log_file: 있음"
        else
            size=$(du -h "$log_file" 2>/dev/null | cut -f1 || echo "알 수 없음")
            echo "  $log_file: $size"
        fi
    else
        echo "  $log_file: 없음"
    fi
done

# 서비스 URL 정보
echo "URL:"
echo "  서버: http://$SERVER_HOST:$SERVER_PORT"
echo "  API: http://$SERVER_HOST:$SERVER_PORT/docs"

# 최종 상태 요약
echo "=========================================="
echo "상태 요약"
echo "=========================================="

# Uvicorn 상태
if [ -f "$PID_FILE" ]; then
    UVICORN_PID=$(cat "$PID_FILE")
    if kill -0 "$UVICORN_PID" 2>/dev/null; then
        SERVER_STATUS="실행 중"
    else
        SERVER_STATUS="중지됨"
    fi
else
    SERVER_STATUS="중지됨"
fi

# Docker 상태
if docker info > /dev/null 2>&1 && docker ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
    DOCKER_STATUS="실행 중"
else
    DOCKER_STATUS="중지됨"
fi

# DB 연결 상태
if (echo > /dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT) 2>/dev/null; then
    DB_STATUS="연결됨"
else
    DB_STATUS="연결 안됨"
fi

echo "서버: $SERVER_STATUS"
echo "Docker: $DOCKER_STATUS"
echo "DB: $DB_STATUS" 