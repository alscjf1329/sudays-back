#!/bin/bash
cd "$ROOT_DIR"

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "📦 프로젝트 루트: $ROOT_DIR"

# ▶ 가상환경 생성
if [ -d "$VENV_DIR" ]; then
    echo "✅ 가상환경 존재함: $VENV_DIR"
else
    echo "🛠️  가상환경 생성 중..."
    python -m venv "$VENV_DIR"
fi

# ▶ 가상환경 활성화 경로 설정
if [[ "$OS_TYPE" == "linux"* ]]; then
    ACTIVATE_PATH="$VENV_DIR/bin/activate"
elif [[ "$OS_TYPE" == "windows" ]]; then
    ACTIVATE_PATH="$VENV_DIR/Scripts/activate"
else
    echo "❌ 지원하지 않는 OS: $OS_TYPE"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    exit 1
fi

# ▶ 가상환경 활성화
if [ -f "$ACTIVATE_PATH" ]; then
    source "$ACTIVATE_PATH"
    echo "✅ 가상환경 활성화됨: $ACTIVATE_PATH"
else
    echo "❌ activate 파일 없음: $ACTIVATE_PATH"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    exit 1
fi

# ▶ pip 업그레이드
echo "────────────────────────────────────────────────────────────────────────"
echo "🔄 pip 업그레이드 중..."
python -m pip install --upgrade pip > /dev/null
echo "✅ pip 업그레이드 완료"

# ▶ 패키지 설치
echo "────────────────────────────────────────────────────────────────────────"
if [ -f "$ROOT_DIR/requirements.txt" ]; then
    echo "📂 requirements.txt 설치 중..."
    pip install -r "$ROOT_DIR/requirements.txt"
    echo "✅ 패키지 설치 완료"
else
    echo "❌ requirements.txt 파일 없음: $ROOT_DIR/requirements.txt"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    exit 1
fi

echo "╚═══════════════════════════════════════════════════════════════════════╝"
