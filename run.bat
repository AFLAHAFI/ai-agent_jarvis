@echo off
title JARVIS Desktop AI
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo ========================================================
echo               STARTING JARVIS DESKTOP AI
echo ========================================================
echo.
".venv\Scripts\python.exe" main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [JARVIS Exited with code %ERRORLEVEL%]
    pause
)
