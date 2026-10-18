@echo off
echo ========================================================
echo   CHAY TOAN BO UNIT TESTS CHO CA 2 SERVICES
echo ========================================================

cd /d %~dp0
call .\venv\Scripts\activate.bat

echo.
echo [1/2] Kiem thu Service 1 (Auth Service)...
python manage.py test core
if %ERRORLEVEL% NEQ 0 (
    echo [THAT BAI] Service 1 co bai test khong dat!
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Kiem thu Service 2 (Product Service)...
python product_service\manage.py test products
if %ERRORLEVEL% NEQ 0 (
    echo [THAT BAI] Service 2 co bai test khong dat!
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo   [THANH CONG] TAT CA CAC BAI KIEM THU DA VUOT QUA (OK)
echo ========================================================
pause
