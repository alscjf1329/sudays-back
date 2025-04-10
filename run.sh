#!/bin/bash

# 도움말 출력
if [ -z "$1" ] || [ "$1" == "--help" ]; then
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║                      사용 방법                         ║"
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║  ./run.sh [옵션]                                       ║"
    echo "║    --dev    개발 모드로 실행 (Docker 컨테이너 포함)    ║"
    echo "║    --prod   운영 모드로 실행                           ║"
    echo "║    --test   테스트 실행                                ║"
    echo "║    --help   도움말 표시                                ║"
    echo "╚════════════════════════════════════════════════════════╝"
    exit 0
fi

# 운영체제 확인
case "$OSTYPE" in
    msys*|win32*|cygwin*)
        # Windows 환경
        ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
        ;;
    *)
        # Linux/Unix/Mac 환경
        ROOT_DIR=$(dirname "$(readlink -f "$0")")
        ;;
esac

source "$ROOT_DIR/bin/venv.sh"
cd "$ROOT_DIR"

ARG="$1"
mode="unknown"

if [ "$ARG" == "--dev" ]; then
    mode="dev"
elif [ "$ARG" == "--prod" ]; then
    mode="prod"
elif [ "$ARG" == "--test" ]; then
    mode="test"
fi

# ========================= 테스트 실행 ============================
echo "╔════════════════════════════════════════════════════════╗"
echo "║ 🧪 테스트를 실행합니다                                 "
echo "╠════════════════════════════════════════════════════════╣"
echo "║ 📁 테스트 디렉토리: $ROOT_DIR/test                     "
echo "╠════════════════════════════════════════════════════════╣"

# 테스트 결과를 임시 파일에 저장
TEST_OUTPUT=$(python -m unittest discover -s test -p "test_*.py" -v 2>&1)
TEST_RESULT=$?

# 테스트 결과 출력을 이쁘게 포맷팅
echo "$TEST_OUTPUT" | while IFS= read -r line; do
    if [[ $line == test* ]]; then
        if [[ $line == *"ok"* ]]; then
            echo "║ ✅ $line"
        elif [[ $line == *"FAIL"* ]]; then
            echo "║ ❌ $line"
        elif [[ $line == *"ERROR"* ]]; then
            echo "║ 💥 $line"
        else
            echo "║ 🔄 $line"
        fi
    else
        echo "║ $line"
    fi
done

echo "╠════════════════════════════════════════════════════════╣"
if [ $TEST_RESULT -eq 0 ]; then
    echo "║ ✨ 모든 테스트가 성공적으로 완료되었습니다!           "
else
    echo "║ 💥 테스트 실행 중 오류가 발생했습니다                "
fi
echo "╚════════════════════════════════════════════════════════╝"

# 테스트 실패시 종료
if [ $TEST_RESULT -ne 0 ]; then
    echo "❌ 테스트 실패로 서비스를 시작할 수 없습니다."
    exit $TEST_RESULT
fi

# 테스트 모드인 경우 여기서 종료
if [ "$mode" == "test" ]; then
    exit $TEST_RESULT
fi

# ========================= 개발 모드 ============================
if [ "$mode" == "dev" ]; then
    ENV_FILE="$ROOT_DIR/env/dev.env"

    echo "╔════════════════════════════════════════════════════════╗"
    echo "║ 🚀 개발 모드로 서비스 실행을 시작합니다              "
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║ 📁 환경 파일: $ENV_FILE"

    # 환경 변수 로드
    if [ -f "$ENV_FILE" ]; then
        set -o allexport
        source "$ENV_FILE"
        set +o allexport
    else
        echo "║ ❌ 환경 파일을 찾을 수 없습니다: $ENV_FILE"
        echo "╚════════════════════════════════════════════════════════╝"
        exit 1
    fi

    # Docker Desktop 실행 여부 확인
    if ! docker info > /dev/null 2>&1; then
        echo "║ ❗ Docker가 실행되고 있지 않거나, 데몬에 연결할 수 없습니다"
        echo "║ ⚠️  Docker Desktop을 먼저 실행해주세요"
        echo "╚════════════════════════════════════════════════════════╝"
        exit 1
    fi

    echo "║ 🔍 Docker 컨테이너 상태 확인 중..."
    if docker ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
        echo "║ ✅ Docker 컨테이너 [$POSTGRES_CONTAINER_NAME] 이미 실행 중"
    else
        echo "║ 🔄 Docker 컨테이너 [$POSTGRES_CONTAINER_NAME] 실행 중..."
        docker-compose --env-file "$ENV_FILE" up -d
    fi

    # 운영체제별 포트 확인 방법
    echo "║ ⏳ DB 포트 응답 대기 중... ($POSTGRES_HOST:$POSTGRES_PORT)"
    MAX_RETRIES=30
    RETRY_COUNT=0
    DB_READY=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        case "$OSTYPE" in
            msys*|win32*|cygwin*)
                # Windows 환경에서 포트 확인
                if (echo > /dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT) 2>/dev/null || \
                   (python -c "import socket; socket.socket().connect(('$POSTGRES_HOST', $POSTGRES_PORT))" 2>/dev/null); then
                    DB_READY=1
                    break
                fi
                ;;
            *)
                # Linux/Unix/Mac 환경에서 포트 확인
                if (echo > /dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT) 2>/dev/null || \
                   (python3 -c "import socket; socket.socket().connect(('$POSTGRES_HOST', $POSTGRES_PORT))" 2>/dev/null); then
                    DB_READY=1
                    break
                fi
                ;;
        esac
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "║ ⏳ DB 연결 시도 중... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done

    if [ $DB_READY -eq 0 ]; then
        echo "║ ❌ DB 연결 실패: $POSTGRES_HOST:$POSTGRES_PORT"
        echo "║ ⚠️  데이터베이스가 실행 중인지 확인해주세요"
        echo "╚════════════════════════════════════════════════════════╝"
        exit 1
    fi

    echo "║ ✨ DB 응답 확인됨 ($POSTGRES_HOST:$POSTGRES_PORT)"
fi

# ========================= 운영 모드 ============================
if [ "$mode" == "prod" ]; then
    ENV_FILE="$ROOT_DIR/env/.env"

    echo "╔════════════════════════════════════════════════════════╗"
    echo "║ 🚀 운영 모드로 서비스 실행을 시작합니다              "
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║ 📁 환경 파일: $ENV_FILE"

    # 환경 변수 로드
    if [ -f "$ENV_FILE" ]; then
        set -o allexport
        source "$ENV_FILE"
        set +o allexport
    else
        echo "║ ❌ 환경 파일을 찾을 수 없습니다: $ENV_FILE"
        echo "╚════════════════════════════════════════════════════════╝"
        exit 1
    fi
fi

# ========================= 잘못된 옵션 처리 ======================
if [ "$mode" == "unknown" ]; then
    echo "❌ 알 수 없는 실행 옵션: $ARG"
    exit 1
fi

# START_MESSAGE 출력
START_MSG=$(grep "START_MESSAGE" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"')

echo "╠════════════════════════════════════════════════════════╣"
echo "║ 🌐 FastAPI 서버 기동 중...                            "
echo "║ 🔗 서버 주소: http://$SERVER_HOST:$SERVER_PORT"
echo "║ 📚 API 명세: http://$SERVER_HOST:$SERVER_PORT/docs"
echo "║ 📖 리덕스 문서: http://$SERVER_HOST:$SERVER_PORT/redoc"
echo "║ ⚙️  서버 설정:"
echo "║   - 호스트: $SERVER_HOST"
echo "║   - 포트: $SERVER_PORT"
echo "║   - 모드: $mode"
echo "║ 💾 데이터베이스 설정:"
echo "║   - 호스트: $POSTGRES_HOST"
echo "║   - 포트: $POSTGRES_PORT"
echo "║   - 데이터베이스: $POSTGRES_DB"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# FastAPI 서버 실행
uvicorn main:app --host "$SERVER_HOST" --port "$SERVER_PORT" --reload