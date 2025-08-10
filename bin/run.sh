#!/bin/bash

cd "$SCRIPT_DIR"
source ./env.sh
source ./venv.sh

cd "$ROOT_DIR"

# ========================= 테스트 실행 ============================
echo "=========================================="
echo "테스트 실행"
echo "=========================================="

TEST_OUTPUT=$(python -m unittest discover -s test -p "test_*.py" -v 2>&1)
TEST_RESULT=$?

if [ "$TEST_RESULT" -eq 0 ]; then
    echo "테스트 완료"
else
    echo "테스트 실패"
    exit "$TEST_RESULT"
fi

if [ "$mode" == "test" ]; then
    exit "$TEST_RESULT"
fi

# ========================= 로컬 모드 ============================
if [ "$mode" == "local" ]; then
    ENV_FILE="$ROOT_DIR/env/local.env"

    if [ -f "$ENV_FILE" ]; then
        set -o allexport
        source "$ENV_FILE"
        set +o allexport
    else
        echo "환경 파일 없음: $ENV_FILE"
        exit 1
    fi
fi

echo "Docker 상태 확인 중..."
if ! docker info > /dev/null 2>&1; then
    echo "Docker 실행 안됨"
    exit 1
fi

if docker ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
    echo "Docker 컨테이너 실행 중"
else
    echo "Docker 컨테이너 시작 중..."
    docker-compose up -d
fi

echo "DB 연결 확인 건너뜀"

cd "$APP_DIR"

# 기존 서버 상태 확인
PID_CHECK_PATHS=(
    "$ROOT_DIR/logs/uvicorn.pid"
    "logs/uvicorn.pid"
    "$APP_DIR/logs/uvicorn.pid"
)

OLD_PID=""
for PID_FILE in "${PID_CHECK_PATHS[@]}"; do
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
            echo "서버가 이미 실행 중입니다 (PID: $OLD_PID)"
            echo "재시작하려면 'restart' 명령어를 사용하세요"
            exit 0
        else
            echo "기존 PID 파일이 있지만 프로세스가 종료됨: $PID_FILE"
            rm -f "$PID_FILE"
        fi
        break
    fi
done

# 서버 기동 로그
echo "=========================================="
echo "서비스 기동"
echo "=========================================="

# Windows 환경에서는 Uvicorn 사용
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    > logs/uvicorn.log 2>&1 &

# 백그라운드 프로세스 ID 저장
UVICORN_PID=$!
echo "백그라운드 프로세스 ID: $UVICORN_PID"

# 현재 디렉토리 확인
echo "현재 디렉토리: $(pwd)"
echo "ROOT_DIR: $ROOT_DIR"
echo "APP_DIR: $APP_DIR"

# 프로세스가 실제로 시작되었는지 확인
sleep 2
if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
    echo "경고: uvicorn 프로세스가 시작되지 않았습니다"
    echo "로그 확인: tail -f logs/uvicorn.log"
    exit 1
fi

# PID 파일 저장 시도 - 여러 경로 시도
PID_PATHS=(
    "$ROOT_DIR/logs/uvicorn.pid"
    "logs/uvicorn.pid"
    "$APP_DIR/logs/uvicorn.pid"
)

for PID_FILE in "${PID_PATHS[@]}"; do
    echo "PID 파일 경로 시도: $PID_FILE"
    
    # 디렉토리 존재 확인
    PID_DIR=$(dirname "$PID_FILE")
    if [ ! -d "$PID_DIR" ]; then
        echo "  디렉토리가 존재하지 않음: $PID_DIR"
        continue
    fi
    
    # 디렉토리 권한 확인
    if [ ! -w "$PID_DIR" ]; then
        echo "  디렉토리에 쓰기 권한이 없음: $PID_DIR"
        continue
    fi
    
    # PID 저장 시도
    echo "$UVICORN_PID" > "$PID_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "  PID 저장 성공: $UVICORN_PID -> $PID_FILE"
        break
    else
        echo "  PID 저장 실패: $PID_FILE"
    fi
done

echo "서비스 기동완료"
echo "PID=$UVICORN_PID"
echo "=========================================="
