#!/bin/bash

cd "$SCRIPT_DIR"
source ./env.sh
source ./venv.sh

cd "$ROOT_DIR"

echo "=========================================="
echo "서비스 중지"
echo "=========================================="

# Uvicorn 프로세스 ID 확인
if [ -f "logs/uvicorn.pid" ]; then
    UVICORN_PID=$(cat logs/uvicorn.pid)
    
    # 프로세스가 실행 중인지 확인
    if kill -0 "$UVICORN_PID" 2>/dev/null; then
        echo "서비스 종료 중... (PID: $UVICORN_PID)"
        
        # Graceful shutdown (SIGTERM)
        kill -TERM "$UVICORN_PID"
        
        # 최대 30초 대기
        MAX_WAIT=30
        WAIT_COUNT=0
        
        while [ "$WAIT_COUNT" -lt "$MAX_WAIT" ]; do
            if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
                echo "서비스 종료 완료"
                break
            fi
            WAIT_COUNT=$((WAIT_COUNT + 1))
            sleep 1
        done
        
        # 여전히 실행 중이면 강제 종료
        if kill -0 "$UVICORN_PID" 2>/dev/null; then
            echo "강제 종료 중..."
            kill -KILL "$UVICORN_PID"
            sleep 2
            
            if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
                echo "강제 종료 완료"
            else
                echo "종료 실패"
            fi
        fi
        
        # PID 파일 삭제
        rm -f logs/uvicorn.pid
        
    else
        echo "서비스가 이미 종료됨"
        rm -f logs/uvicorn.pid
    fi
else
    echo "PID 파일 없음"
fi



echo "=========================================="
echo "중지 완료"
echo "==========================================" 