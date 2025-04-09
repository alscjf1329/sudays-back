#!/bin/bash

# 루트 디렉토리 설정
if [ -z "$ROOT_DIR" ]; then
    ROOT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
fi

# 가상환경 체크 및 생성
if [ ! -f "$ROOT_DIR/.venv/bin/activate" ]; then
    echo "╔════════════════════════════════════════════╗"
    echo "║ 🔨 가상환경을 생성합니다...               ║"
    echo "╚════════════════════════════════════════════╝"
    python -m venv "$ROOT_DIR/.venv"
fi

# 가상환경 활성화
echo "╔════════════════════════════════════════════╗"
echo "║ ✨ 가상환경을 활성화합니다...             ║" 
echo "╚════════════════════════════════════════════╝"
source "$ROOT_DIR/.venv/bin/activate"

# 패키지 설치 및 업그레이드
echo "╔════════════════════════════════════════════╗"
echo "║ 🔄 패키지를 업데이트합니다...             ║"
echo "╚════════════════════════════════════════════╝"
python -m pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements.txt"

# 테스트 주석 제거
# echo "테스트를 실행합니다..."
# pytest "$ROOT_DIR/test/utils"
# if [ $? -ne 0 ]; then
#     echo "테스트 실패! 자세한 내용은 위의 로그를 확인하세요."
#     read -p "계속하려면 아무 키나 누르세요..."
#     exit 1
# fi 