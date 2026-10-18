@echo off
title Service 1: Authentication Service (Port 8000)
echo ========================================================
echo   KHOI DONG SERVICE 1: AUTH SERVICE (BAI 1 ^& 2)
echo   Cong: http://127.0.0.1:8000
echo   Swagger UI: http://127.0.0.1:8000/swagger/
echo ========================================================

cd /d %~dp0
call .\venv\Scripts\activate.bat
python manage.py runserver 8000
pause
