@echo off
title Service 2: Product Management Service (Port 8001)
echo ========================================================
echo   KHOI DONG SERVICE 2: PRODUCT SERVICE (BAI 3 - SOA)
echo   Cong: http://127.0.0.1:8001
echo   Swagger UI: http://127.0.0.1:8001/swagger/
echo   Ket noi Auth Service: http://127.0.0.1:8000/auth
echo ========================================================

cd /d %~dp0
call .\venv\Scripts\activate.bat
python product_service\manage.py runserver 8001
pause
