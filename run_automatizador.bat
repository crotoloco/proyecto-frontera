@echo off
REM Wrapper para ejecutar la automatización y guardar logs con timestamp
+setlocal enabledelayedexpansion
+set LOGDIR=C:\Users\USUARIO\Downloads\frontera_living_python\logs
+if not exist "%LOGDIR%" mkdir "%LOGDIR%"
+set d=%DATE%
+set t=%TIME%
+set d=%d:/=-%
+set t=%t::=-%
+set t=%t:.=-%
+set TIMESTAMP=%d%_%t%
+set TIMESTAMP=%TIMESTAMP: =%
+"C:\Program Files\Python311\python.exe" "C:\Users\USUARIO\Downloads\frontera_living_python\scripts\AUTOMATIZAR_TODO.py" >> "%LOGDIR%\automation_%TIMESTAMP%.log" 2>&1
+endlocal
