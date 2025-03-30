@echo off

:: 도움말 출력 조건
if "%1"=="" goto showHelp
if "%1"=="--help" goto showHelp

:: 정상 실행 로직
goto continueRun

:showHelp
echo 사용법: run.bat [옵션]
echo.
echo 옵션:
echo   --dev    개발 모드로 실행 (Docker 컨테이너 포함)
echo   --prod   운영 모드로 실행
echo   --help   도움말 표시
exit /b 0

:continueRun
:: 현재 디렉토리 설정
set ROOT_DIR=%~dp0
call %ROOT_DIR%/bin/venv.bat

cd %ROOT_DIR%

:: dev 모드 확인
if "%1"=="--dev" (
    set mode=dev
    :: dev.env 파일 사용
    set ENV_FILE=%ROOT_DIR%/env/dev.env
    :: Docker 컨테이너 실행 (dev 모드일 때만)
    echo Docker 컨테이너를 시작합니다...
    call docker-compose --env-file %ENV_FILE% up -d
) else if "%1"=="--prod" (
    set mode=prod
    :: 기본 .env 파일 사용
    set ENV_FILE=%ROOT_DIR%/env/.env
)

for /f "tokens=2 delims==" %%a in ('type %ENV_FILE% ^| findstr "START_MESSAGE"') do echo %%a

:: FastAPI 서버 실행
echo FastAPI 서버를 시작합니다...
call uvicorn main:app --reload

echo http://localhost:8000/docs
echo http://localhost:8000/redoc

pause