#!/bin/bash

cd "$SCRIPT_DIR"
source ./env.sh
source ./venv.sh

cd "$ROOT_DIR"

# ========================= 테스트 실행 ============================
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "🧪 테스트를 실행합니다"
echo "────────────────────────────────────────────────────────────────────────"
echo "📁 테스트 디렉토리: $ROOT_DIR/test"
echo "────────────────────────────────────────────────────────────────────────"

TEST_OUTPUT=$(python -m unittest discover -s test -p "test_*.py" -v 2>&1)
TEST_RESULT=$?

echo "$TEST_OUTPUT" | while IFS= read -r line; do
    if [[ $line == test* ]]; then
        if [[ $line == *"ok"* ]]; then
            echo "✅ $line"
        elif [[ $line == *"FAIL"* ]]; then
            echo "❌ $line"
        elif [[ $line == *"ERROR"* ]]; then
            echo "💥 $line"
        else
            echo "🔄 $line"
        fi
    else
        echo "$line"
    fi
done

echo "────────────────────────────────────────────────────────────────────────"
if [ "$TEST_RESULT" -eq 0 ]; then
    echo "✨ 모든 테스트가 성공적으로 완료되었습니다!"
else
    echo "💥 테스트 실행 중 오류가 발생했습니다"
fi
echo "╚═══════════════════════════════════════════════════════════════════════╝"

if [ "$TEST_RESULT" -ne 0 ]; then
    echo "❌ 테스트 실패로 서비스를 시작할 수 없습니다."
    exit "$TEST_RESULT"
fi

if [ "$mode" == "test" ]; then
    exit "$TEST_RESULT"
fi

# ========================= 로컬 모드 ============================
if [ "$mode" == "local" ]; then
    ENV_FILE="$ROOT_DIR/env/local.env"

    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "🚀 로컬 모드로 서비스 실행을 시작합니다"
    echo "────────────────────────────────────────────────────────────────────────"
    echo "📁 환경 파일: $ENV_FILE"

    if [ -f "$ENV_FILE" ]; then
        set -o allexport
        source "$ENV_FILE"
        set +o allexport
    else
        echo "❌ 환경 파일을 찾을 수 없습니다: $ENV_FILE"
        echo "╚═══════════════════════════════════════════════════════════════════════╝"
        exit 1
    fi

    echo "────────────────────────────────────────────────────────────────────────"
    echo "🔍 Docker 상태 확인 중..."
    if ! docker info > /dev/null 2>&1; then
        echo "❗ Docker가 실행 중이 아니거나 데몬에 연결할 수 없습니다"
        echo "⚠️  Docker Desktop을 먼저 실행해주세요"
        echo "╚═══════════════════════════════════════════════════════════════════════╝"
        exit 1
    fi

    if docker ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
        echo "✅ Docker 컨테이너 [$POSTGRES_CONTAINER_NAME] 이미 실행 중"
    else
        echo "🔄 Docker 컨테이너 [$POSTGRES_CONTAINER_NAME] 실행 중..."
        docker-compose --env-file "$ENV_FILE" up -d
    fi

    echo "────────────────────────────────────────────────────────────────────────"
    echo "⏳ DB 포트 응답 대기 중... ($POSTGRES_HOST:$POSTGRES_PORT)"
    MAX_RETRIES=30
    RETRY_COUNT=0
    DB_READY=0

    while [ "$RETRY_COUNT" -lt "$MAX_RETRIES" ]; do
        if (echo > /dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT) 2>/dev/null || \
           (python3 -c "import socket; socket.socket().connect((\"$POSTGRES_HOST\", $POSTGRES_PORT))" 2>/dev/null); then
            DB_READY=1
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "⏳ DB 연결 시도 중... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done

    if [ "$DB_READY" -eq 0 ]; then
        echo "❌ DB 연결 실패: $POSTGRES_HOST:$POSTGRES_PORT"
        echo "⚠️  데이터베이스가 실행 중인지 확인해주세요"
        echo "╚═══════════════════════════════════════════════════════════════════════╝"
        exit 1
    fi

    echo "✨ DB 응답 확인됨 ($POSTGRES_HOST:$POSTGRES_PORT)"

    cd "$APP_DIR"

    # 서버 기동 로그
    echo "────────────────────────────────────────────────────────────────────────"
    echo "🌐 FastAPI 서버 기동 중..."
    echo "🔗 서버 주소:    http://$SERVER_HOST:$SERVER_PORT"
    echo "📚 API 명세:    http://$SERVER_HOST:$SERVER_PORT/docs"
    echo "📖 리덕스 문서: http://$SERVER_HOST:$SERVER_PORT/redoc"
    echo "────────────────────────────────────────────────────────────────────────"
    echo "⚙️  서버 설정"
    echo "   - 모드:         $mode"
    echo "   - 호스트:       $SERVER_HOST"
    echo "   - 포트:         $SERVER_PORT"
    echo "────────────────────────────────────────────────────────────────────────"
    echo "💾 데이터베이스 설정"
    echo "   - 호스트:       $POSTGRES_HOST"
    echo "   - 포트:         $POSTGRES_PORT"
    echo "   - 데이터베이스: $POSTGRES_DB"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    echo ""

    uvicorn main:app --host "$SERVER_HOST" --port "$SERVER_PORT" --reload
fi
