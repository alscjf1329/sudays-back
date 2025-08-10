#!/bin/bash

echo "서버 상태 확인 테스트"
echo "===================="

if [ -f "logs/uvicorn.pid" ]; then
    OLD_PID=$(cat logs/uvicorn.pid)
    echo "PID 파일에서 읽은 PID: $OLD_PID"
    
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "서버가 이미 실행 중입니다 (PID: $OLD_PID)"
        echo "재시작하려면 'restart' 명령어를 사용하세요"
    else
        echo "기존 PID 파일이 있지만 프로세스가 종료됨"
        echo "PID 파일을 삭제합니다"
        rm -f logs/uvicorn.pid
    fi
else
    echo "PID 파일이 없습니다"
fi 