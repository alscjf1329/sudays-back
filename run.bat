@echo off
setlocal enabledelayedexpansion

:: 도움말 출력
if "%1"=="" goto showHelp
if "%1"=="--help" goto showHelp

goto continueRun

:showHelp
echo ============================================================
echo [ USAGE ] run.bat [옵션]
echo ------------------------------------------------------------
echo   --dev    개발 모드로 실행 (Docker 컨테이너 포함)
echo   --prod   운영 모드로 실행
echo   --help   도움말 표시
echo ============================================================
exit /b 0

:continueRun
set ROOT_DIR=%~dp0
call %ROOT_DIR%/bin/venv.bat
cd /d %ROOT_DIR%

set ARG=%1
set mode=unknown

if "%ARG%"=="--dev" (
    set mode=dev
)
if "%ARG%"=="--prod" (
    set mode=prod
)

:: ========================= 개발 모드 ============================
if "%mode%"=="dev" (
    set ENV_FILE=%ROOT_DIR%/env/dev.env
    set CONTAINER_NAME=db

    echo ============================================================
    echo [INFO] 개발 모드로 서비스 실행 시작
    echo ------------------------------------------------------------
    echo [INFO] 환경 파일 로딩: %ENV_FILE%
    echo [INFO] Docker 컨테이너 상태 확인 중...

    docker ps | findstr "%CONTAINER_NAME%" >nul
    if %errorlevel%==0 (
        echo [OK] Docker 컨테이너 [%CONTAINER_NAME%] 이미 실행 중
    ) else (
        echo [BOOT] Docker 컨테이너 [%CONTAINER_NAME%] 실행 중...
        docker-compose --env-file %ENV_FILE% up -d
    )

    echo [WAIT] DB 포트 응답 대기 중... (5432)
    :waitdb
    timeout /t 1 >nul
    powershell -command "(Test-NetConnection -ComputerName 127.0.0.1 -Port 5432).TcpTestSucceeded" | findstr "True" >nul
    if %errorlevel%==1 goto waitdb
    echo [READY] DB 응답 확인됨 (localhost:5432)
)

:: ========================= 운영 모드 ============================
if "%mode%"=="prod" (
    set ENV_FILE=%ROOT_DIR%/env/.env

    echo ============================================================
    echo [INFO] 운영 모드로 서비스 실행 시작
    echo ------------------------------------------------------------
    echo [INFO] 환경 파일 로딩: %ENV_FILE%
)

:: ========================= 잘못된 옵션 처리 ======================
if "%mode%"=="unknown" (
    echo ❌ 알 수 없는 실행 옵션: %ARG%
    goto showHelp
)

:: START_MESSAGE 출력
for /f "tokens=2 delims==" %%a in ('type %ENV_FILE% ^| findstr "START_MESSAGE"') do (
    set MSG=%%a
    set MSG=!MSG:"=!
    echo !MSG!
)

:: FastAPI 서버 실행
echo ------------------------------------------------------------
echo [ACTION] FastAPI 서버 기동 중...
call uvicorn main:app --reload

:: 문서 안내
echo ------------------------------------------------------------
echo [DOCS] API 명세 보기: http://localhost:8000/docs
echo [DOCS] 리덕 문서 보기: http://localhost:8000/redoc
echo ============================================================

pause
