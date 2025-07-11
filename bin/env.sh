#!/bin/bash

# 경로 설정
export SCRIPT_DIR=$(pwd)
export ROOT_DIR="$SCRIPT_DIR/.."
export APP_DIR="$ROOT_DIR/app"

export PYTHONPATH="$APP_DIR"
cd "$ROOT_DIR"

# 설정 정보 출력
echo "서버 정보 ... (생략)"

uvicorn app.main:app --host "$SERVER_HOST" --port "$SERVER_PORT" --reload