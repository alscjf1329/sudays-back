@echo off

:: 루트 디렉토리 설정
set ROOT_DIR=%~dp0\..

:: 가상환경이 없으면 생성
IF NOT EXIST "%ROOT_DIR%\.venv\Scripts\activate.bat" (
    echo 가상환경을 생성합니다...
    call python -m venv %ROOT_DIR%\.venv
)

:: 가상환경 활성화 및 패키지 설치
echo 가상환경을 활성화합니다...
call %ROOT_DIR%\.venv\Scripts\activate

:: 패키지 업그레이드
echo 패키지 업그레이드 중...
call python -m pip install --upgrade pip

echo 필요한 패키지를 설치합니다...
call pip install -r %ROOT_DIR%\requirements.txt

:: 테스트 실행
@REM echo 테스트를 실행합니다...
@REM call pytest %ROOT_DIR%\test\utils
@REM IF %ERRORLEVEL% NEQ 0 (
@REM     echo 테스트 실패! 자세한 내용은 위의 로그를 확인하세요.
@REM     pause
@REM     exit /b 1
@REM )

