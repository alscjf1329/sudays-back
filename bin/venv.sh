#!/bin/bash
cd "$ROOT_DIR"

echo "=========================================="
echo "가상환경 설정"
echo "=========================================="

# ▶ 가상환경 생성
if [ -d "$VENV_DIR" ]; then
    echo "가상환경 존재함"
else
    echo "가상환경 생성 중..."
    python -m venv "$VENV_DIR"
fi

# ▶ 가상환경 활성화 경로 설정
if [[ "$OS_TYPE" == "linux"* ]]; then
    ACTIVATE_PATH="$VENV_DIR/bin/activate"
elif [[ "$OS_TYPE" == "windows" ]]; then
    ACTIVATE_PATH="$VENV_DIR/Scripts/activate"
else
    echo "지원하지 않는 OS: $OS_TYPE"
    exit 1
fi

# ▶ 가상환경 활성화
if [ -f "$ACTIVATE_PATH" ]; then
    source "$ACTIVATE_PATH"
    echo "가상환경 활성화됨"
else
    echo "activate 파일 없음: $ACTIVATE_PATH"
    exit 1
fi

# ▶ pip 업그레이드
echo "pip 업그레이드 중..."
python -m pip install --upgrade pip > /dev/null
echo "pip 업그레이드 완료"

# ▶ 패키지 설치
if [ -f "$ROOT_DIR/requirements.txt" ]; then
    echo "패키지 설치 중..."
    pip install -r "$ROOT_DIR/requirements.txt" > /dev/null 2>&1
    echo "패키지 설치 완료"
else
    echo "requirements.txt 파일 없음: $ROOT_DIR/requirements.txt"
    exit 1
fi
