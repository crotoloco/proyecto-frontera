@echo off
setlocal

set "ROOT=C:\Users\USUARIO\Downloads\frontera_living_python"
set "PYTHON=%ROOT%\.venv\Scripts\python.exe"

if not exist "%PYTHON%" set "PYTHON=C:\Program Files\Python311\python.exe"
if not exist "%PYTHON%" (
    echo No se encontro Python.
    pause
    exit /b 1
)

start "Centro de Control" /min "%PYTHON%" "%ROOT%\centro_control\app.py"
ping 127.0.0.1 -n 3 >nul
start "" "http://127.0.0.1:5000/login"

endlocal
