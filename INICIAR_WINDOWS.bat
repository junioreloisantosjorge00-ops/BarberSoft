@echo off
title BarberSoft
echo Instalando Flask (solo la primera vez)...
python -m pip install flask
start "" http://127.0.0.1:5000
echo.
echo BarberSoft esta encendido. NO cierres esta ventana.
python app.py
pause
