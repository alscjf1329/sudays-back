#!/bin/bash

# Sudays Backend Service Management
# 사용법: ./make.sh [명령어]

# 색상 정의 (호환성을 위해 비활성화)
RED=''
GREEN=''
YELLOW=''
BLUE=''
PURPLE=''
CYAN=''
NC=''

# 스크립트 디렉토리 설정
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$BIN_DIR/.."

# 로그 함수
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${PURPLE}🚀 $1${NC}"
}

# 도움말 함수
show_help() {
    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "🚀 Sudays Backend Service Management"
    echo "────────────────────────────────────────────────────────────────────────"
    echo "사용법: ./make.sh [명령어]"
    echo ""
    echo "📋 사용 가능한 명령어:"
    echo "   ${CYAN}help${NC}              # 도움말 표시"
    echo "   ${CYAN}start${NC}             # 서비스 시작"
    echo "   ${CYAN}stop${NC}              # 서비스 중지"
    echo "   ${CYAN}restart${NC}           # 서비스 재시작"
    echo "   ${CYAN}status${NC}            # 상태 확인"
    echo "   ${CYAN}test${NC}              # 테스트 실행"
    echo "   ${CYAN}install${NC}           # 의존성 설치"
    echo "   ${CYAN}setup${NC}             # 초기 설정"
    echo "   ${CYAN}docker-up${NC}         # Docker 시작"
    echo "   ${CYAN}docker-down${NC}       # Docker 중지"
    echo "   ${CYAN}docker-restart${NC}    # Docker 재시작"
    echo "   ${CYAN}docker-logs${NC}       # Docker 로그"
    echo "   ${CYAN}log${NC}               # 로그 확인"
    echo "   ${CYAN}log-error${NC}         # 에러 로그 확인"
    echo "   ${CYAN}log-access${NC}        # 접근 로그 확인"
    echo "   ${CYAN}info${NC}              # 시스템 정보"
    echo ""
    echo "예시:"
    echo "   ./make.sh start    # 서비스 시작"
    echo "   ./make.sh stop     # 서비스 중지"
    echo "   ./make.sh status   # 상태 확인"
    echo "   ./make.sh restart  # 서비스 재시작"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
}

# 서비스 관리 함수들
start_service() {
    log_header "서비스를 시작합니다..."
    bash "$BIN_DIR/run.sh"
}

stop_service() {
    log_header "서비스를 중지합니다..."
    bash "$BIN_DIR/stop.sh"
}

restart_service() {
    log_header "서비스를 재시작합니다..."
    stop_service
    start_service
}

status_service() {
    log_header "서비스 상태를 확인합니다..."
    bash "$BIN_DIR/status.sh"
}

# 개발 관련 함수들
run_tests() {
    log_header "테스트를 실행합니다..."
    cd "$APP_DIR" && python -m unittest discover -s test -p "test_*.py" -v
}

# 설치 및 설정 함수들
install_deps() {
    log_header "의존성을 설치합니다..."
    pip install -r requirements.txt > /dev/null 2>&1
}

setup_project() {
    log_header "초기 설정을 수행합니다..."
    mkdir -p "$LOG_DIR"
    mkdir -p "$APP_DIR/uploads/images"
    log_success "디렉토리 생성 완료"
}

# Docker 관련 함수들
docker_up() {
    log_header "Docker 컨테이너를 시작합니다..."
    docker-compose up -d
}

docker_down() {
    log_header "Docker 컨테이너를 중지합니다..."
    docker-compose down
}

docker_restart() {
    log_header "Docker 컨테이너를 재시작합니다..."
    docker-compose restart
}

docker_logs() {
    log_header "Docker 컨테이너 로그를 확인합니다..."
    docker-compose logs -f
}



# 로그 관련 함수들
show_log() {
    echo "=========================================="
    echo "로그 확인"
    echo "=========================================="
    LOG_DIR=${LOG_DIR:-"$LOG_DIR"}
    APP_LOG_FILE=${APP_LOG_FILE:-"sudays.log"}
    LOG_FILE_PATH="$LOG_DIR/$APP_LOG_FILE"
    
    if [ -f "$LOG_FILE_PATH" ]; then
        tail -f "$LOG_FILE_PATH"
    else
        echo "로그 파일 없음: $LOG_FILE_PATH"
    fi
}

show_error_log() {
    echo "=========================================="
    echo "에러 로그 확인"
    echo "=========================================="
    LOG_DIR=${LOG_DIR:-"$LOG_DIR"}
    ERROR_LOG_FILE=${ERROR_LOG_FILE:-"error.log"}
    LOG_FILE_PATH="$LOG_DIR/$ERROR_LOG_FILE"
    
    if [ -f "$LOG_FILE_PATH" ]; then
        tail -f "$LOG_FILE_PATH"
    else
        echo "에러 로그 파일 없음: $LOG_FILE_PATH"
    fi
}

show_access_log() {
    echo "=========================================="
    echo "접근 로그 확인"
    echo "=========================================="
    LOG_DIR=${LOG_DIR:-"$LOG_DIR"}
    ACCESS_LOG_FILE=${ACCESS_LOG_FILE:-"access.log"}
    LOG_FILE_PATH="$LOG_DIR/$ACCESS_LOG_FILE"
    
    if [ -f "$LOG_FILE_PATH" ]; then
        tail -f "$LOG_FILE_PATH"
    else
        echo "접근 로그 파일 없음: $LOG_FILE_PATH"
    fi
}

# 시스템 정보 함수
show_info() {
    echo "=========================================="
    echo "시스템 정보"
    echo "=========================================="
    echo "Python 버전:"
    python --version
    echo ""
    echo "Docker 버전:"
    docker --version
    echo ""
    echo "Docker Compose 버전:"
    docker-compose --version
    echo ""
    echo "현재 디렉토리:"
    pwd
    echo ""
    echo "환경 변수:"
    echo "  LOG_DIR: $LOG_DIR"
    echo "  PID_DIR: $PID_DIR"
    echo "  VENV_DIR: $VENV_DIR"
    echo "  PYTHONPATH: $PYTHONPATH"
    echo "  APP_DIR: $APP_DIR"
    echo "  BIN_DIR: $BIN_DIR"
}

# 메인 로직
case "$1" in
    "help"|"")
        show_help
        ;;
    "setup")
        setup_project
        ;;
    "docker-up")
        docker_up
        ;;
    "docker-down")
        docker_down
        ;;
    "docker-restart")
        docker_restart
        ;;
    "docker-logs")
        docker_logs
        ;;
    "stop")
        stop_service
        ;;
    "start")
        start_service
        ;;
    "restart")
        restart_service
        ;;
    "status")
        status_service
        ;;
    "test")
        run_tests
        ;;
    "install")
        install_deps
        ;;
    "log")
        show_log
        ;;
    "log-error")
        show_error_log
        ;;
    "log-access")
        show_access_log
        ;;
    "info")
        show_info
        ;;
    *)
        log_error "알 수 없는 명령어: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 