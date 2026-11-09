@echo off
title Service 4: Reporting Service (Port 8003)
echo ========================================================
echo   KHOI DONG SERVICE 4: REPORTING SERVICE (BAI 5 - SOA)
echo   Cong: http://127.0.0.1:8003
echo   Swagger UI: http://127.0.0.1:8003/swagger/
echo   Ket noi Auth Service:    http://127.0.0.1:8000/auth
echo   Ket noi Product Service: http://127.0.0.1:8001/products
echo   Ket noi Order Service:   http://127.0.0.1:8002/orders
echo ========================================================

cd /d %~dp0
call .\venv\Scripts\activate.bat
python report_service\manage.py runserver 8003
pause

