#!/bin/bash

cd "$SCRIPT_DIR"
source ./env.sh
source ./venv.sh

cd "$ROOT_DIR"

echo "=========================================="
echo "서비스 재시작"
echo "=========================================="

# 현재 실행 중인 서비스 중지
if [ -f "logs/uvicorn.pid" ]; then
    UVICORN_PID=$(cat logs/uvicorn.pid)
    if kill -0 "$UVICORN_PID" 2>/dev/null; then
        echo "기존 서비스 종료 중... (PID: $UVICORN_PID)"
        kill -TERM "$UVICORN_PID"
        
        # 최대 15초 대기
        MAX_WAIT=15
        WAIT_COUNT=0
        
        while [ "$WAIT_COUNT" -lt "$MAX_WAIT" ]; do
            if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
                break
            fi
            WAIT_COUNT=$((WAIT_COUNT + 1))
            sleep 1
        done
        
        # 여전히 실행 중이면 강제 종료
        if kill -0 "$UVICORN_PID" 2>/dev/null; then
            kill -KILL "$UVICORN_PID"
            sleep 2
        fi
        
        rm -f logs/uvicorn.pid
    fi
fi

echo "테스트 실행 중..."
TEST_OUTPUT=$(python -m unittest discover -s test -p "test_*.py" -v 2>&1)
TEST_RESULT=$?

if [ "$TEST_RESULT" -eq 0 ]; then
    echo "테스트 완료"
else
    echo "테스트 실패"
    exit "$TEST_RESULT"
fi

echo "Docker 상태 확인 중..."
if ! docker info > /dev/null 2>&1; then
    echo "Docker 실행 안됨"
    exit 1
fi

# Docker 컨테이너 재시작
if docker ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
    echo "Docker 컨테이너 재시작 중..."
    docker-compose --env-file "$ENV_FILE" restart
else
    echo "Docker 컨테이너 시작 중..."
    docker-compose --env-file "$ENV_FILE" up -d
fi

echo "DB 연결 확인 중..."
MAX_RETRIES=30
RETRY_COUNT=0
DB_READY=0

while [ "$RETRY_COUNT" -lt "$MAX_RETRIES" ]; do
    if (echo > /dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT) 2>/dev/null || \
        (python3 -c "import socket; socket.socket().connect((\"$POSTGRES_HOST\", $POSTGRES_PORT))" 2>/dev/null); then
        DB_READY=1
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ "$DB_READY" -eq 0 ]; then
    echo "DB 연결 실패"
    exit 1
fi

echo "DB 연결 완료"

cd "$APP_DIR"

# 서버 재시작
echo "서버 재시작 중..."

# Windows 환경에서는 Uvicorn 사용 (프로세스명 지정)
python -c "
import subprocess
import sys
import os

# 프로세스명을 sudays_diary로 지정
os.environ['_'] = 'sudays_diary'

cmd = [
    sys.executable, '-m', 'uvicorn', 'main:app',
    '--host', '0.0.0.0',
    '--port', '8000',
    '--reload',
    '--log-level', 'info'
]

# 백그라운드에서 실행
process = subprocess.Popen(
    cmd,
    stdout=open('logs/uvicorn.log', 'w'),
    stderr=subprocess.STDOUT,
    env=os.environ
)

# PID 저장
with open('logs/uvicorn.pid', 'w') as f:
    f.write(str(process.pid))

print(f'서비스 재시작완료')
print(f'PID={process.pid}')
print('==========================================')
" &

# 백그라운드 프로세스 ID 저장
UVICORN_PID=$!
echo $UVICORN_PID > logs/uvicorn.pid

# 프로세스명 기록
echo "sudays_diary" > logs/process_name.txt

echo "서비스 재시작완료"
echo "PID=$UVICORN_PID"
echo "==========================================" 