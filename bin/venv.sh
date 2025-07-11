#!/bin/bash

# 가상 환경 디렉토리 설정
VENV_DIR="$ROOT_DIR/.venv"

# OS 타입 확인
case "$OSTYPE" in
    msys*|win32*|cygwin*)
        # Windows 환경
        if [ -d "$VENV_DIR" ]; then
            echo "가상 환경이 이미 존재합니다."
        else
            echo "가상 환경을 생성합니다..."
            python -m venv "$VENV_DIR"
        fi
        
        # Windows에서 가상 환경 활성화
        if [ -f "$VENV_DIR/Scripts/activate" ]; then
            source "$VENV_DIR/Scripts/activate"
        else
            echo "가상 환경 활성화 파일을 찾을 수 없습니다."
            exit 1
        fi
        ;;
    linux*|darwin*|freebsd*|openbsd*|netbsd*)
        # Linux/Unix/Mac 환경
        if [ -d "$VENV_DIR" ]; then
            echo "가상 환경이 이미 존재합니다."
        else
            echo "가상 환경을 생성합니다..."
            python3 -m venv "$VENV_DIR"
        fi
        
        # Linux/Unix/Mac에서 가상 환경 활성화
        if [ -f "$VENV_DIR/bin/activate" ]; then
            source "$VENV_DIR/bin/activate"
        else
            echo "가상 환경 활성화 파일을 찾을 수 없습니다."
            exit 1
        fi
        ;;
    *)
        echo "지원하지 않는 운영체제입니다: $OSTYPE"
        exit 1
        ;;
esac

# 필요한 패키지 설치
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt 파일을 찾을 수 없습니다."
    exit 1
fi

# 패키지 설치 및 업그레이드
echo "╔════════════════════════════════════════════╗"
echo "║ 🔄 패키지를 업데이트합니다...             ║"
echo "╚════════════════════════════════════════════╝"

# pip 업그레이드
python -m pip install --upgrade pip

# 프로젝트 requirements 설치
if [ -f "$ROOT_DIR/requirements.txt" ]; then
    pip install -r "$ROOT_DIR/requirements.txt"
else
    echo "프로젝트 requirements.txt 파일을 찾을 수 없습니다."
    exit 1
fi

# 테스트 주석 제거
# echo "테스트를 실행합니다..."
# pytest "$PROJECT_ROOT/test/utils"
# if [ $? -ne 0 ]; then
#     echo "테스트 실패! 자세한 내용은 위의 로그를 확인하세요."
#     read -p "계속하려면 아무 키나 누르세요..."
#     exit 1
# fi 