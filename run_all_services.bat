@echo off
echo ========================================================
echo   KHOI DONG DONG THOI CA 3 DICH VU TRONG KIEN TRUC SOA
echo   - Service 1 (Auth):    http://127.0.0.1:8000
echo   - Service 2 (Product): http://127.0.0.1:8001
echo   - Service 3 (Order):   http://127.0.0.1:8002
echo ========================================================

start "Auth Service (Port 8000)" cmd /k "call run_auth_service.bat"
timeout /t 2 /nobreak >nul
start "Product Service (Port 8001)" cmd /k "call run_product_service.bat"
timeout /t 2 /nobreak >nul
start "Order Service (Port 8002)" cmd /k "call run_order_service.bat"

echo.
echo Ca 3 dich vu da duoc bat trong 3 cua so rieng biet!
