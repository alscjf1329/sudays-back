#!/bin/bash

# ▶ 실행 모드 설정 (local/dev/prod 중 하나)
export mode="local"  # <-- 필요 시 변경

# ▶ 기본 유효성 검사
if [ "$mode" == "unknown" ]; then
    echo "❌ 알 수 없는 실행 옵션입니다: $mode"
    exit 1
fi

# ▶ 환경별 설정
if [ "$mode" == "prod" ]; then
    export ROOT_DIR="/app/sudays/diary/sudays-back"
    export OS_TYPE="linux"
    export ENV_FILE="$ROOT_DIR/env/prod.env"
elif [ "$mode" == "dev" ]; then
    export ROOT_DIR="/c/Users/SheepDuck/Desktop/project/sudays/sudays-back"
    export OS_TYPE="windows"
    export ENV_FILE="$ROOT_DIR/env/dev.env"
elif [ "$mode" == "local" ]; then
    export ROOT_DIR="/c/Users/SheepDuck/Desktop/project/sudays/sudays-back"
    export OS_TYPE="windows"
    export ENV_FILE="$ROOT_DIR/env/local.env"
fi

# ▶ 경로 설정
export SCRIPT_DIR="$ROOT_DIR/bin"
export APP_DIR="$ROOT_DIR/app"
export VENV_DIR="$ROOT_DIR/.venv"
export PYTHONPATH="$APP_DIR"

# ▶ 시작 로그 출력
echo "=========================================="
echo "환경 설정"
echo "=========================================="

# ▶ 환경 변수 로드
if [ -f "$ENV_FILE" ]; then
    set -o allexport
    source "$ENV_FILE"
    set +o allexport
    echo "환경 설정 완료"
else
    echo "환경 파일 없음: $ENV_FILE"
    exit 1
fi
