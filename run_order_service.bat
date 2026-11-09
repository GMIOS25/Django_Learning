@echo off
title Service 3: Order Management Service (Port 8002)
echo ========================================================
echo   KHOI DONG SERVICE 3: ORDER SERVICE (BAI 4 - SOA)
echo   Cong: http://127.0.0.1:8002
echo   Swagger UI: http://127.0.0.1:8002/swagger/
echo   Ket noi Auth Service: http://127.0.0.1:8000/auth
echo   Ket noi Product Service: http://127.0.0.1:8001/products
echo ========================================================

cd /d %~dp0
call .\venv\Scripts\activate.bat
python order_service\manage.py runserver 8002
pause

