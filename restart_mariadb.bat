@echo off
echo ========================================
echo MariaDB/MySQL 서비스 재시작
echo ========================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [오류] 관리자 권한이 필요합니다.
    echo 이 파일을 우클릭하고 "관리자 권한으로 실행"을 선택하세요.
    pause
    exit /b 1
)

echo MariaDB 서비스를 찾는 중...
echo.

REM MariaDB 서비스 확인
sc query MariaDB >nul 2>&1
if %errorLevel% equ 0 (
    echo [발견] MariaDB 서비스 발견
    echo MariaDB 서비스를 재시작합니다...
    net stop MariaDB
    timeout /t 2 /nobreak >nul
    net start MariaDB
    echo.
    echo [완료] MariaDB 서비스가 재시작되었습니다.
    goto :end
)

REM MySQL 서비스 확인
sc query MySQL >nul 2>&1
if %errorLevel% equ 0 (
    echo [발견] MySQL 서비스 발견
    echo MySQL 서비스를 재시작합니다...
    net stop MySQL
    timeout /t 2 /nobreak >nul
    net start MySQL
    echo.
    echo [완료] MySQL 서비스가 재시작되었습니다.
    goto :end
)

REM MySQL80 서비스 확인
sc query MySQL80 >nul 2>&1
if %errorLevel% equ 0 (
    echo [발견] MySQL80 서비스 발견
    echo MySQL80 서비스를 재시작합니다...
    net stop MySQL80
    timeout /t 2 /nobreak >nul
    net start MySQL80
    echo.
    echo [완료] MySQL80 서비스가 재시작되었습니다.
    goto :end
)

echo [오류] MariaDB 또는 MySQL 서비스를 찾을 수 없습니다.
echo.
echo 사용 가능한 서비스를 확인하려면 다음 명령을 실행하세요:
echo   sc query | findstr /i "mysql mariadb"
echo.

:end
echo.
echo ========================================
echo 서비스 상태 확인:
sc query | findstr /i "mysql mariadb"
echo.
pause


