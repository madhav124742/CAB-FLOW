@echo off
title Cab Prediction System - Launcher
echo ===================================================
echo   Starting Cab Prediction System Web Application
echo ===================================================
echo.
cd /d "%~dp0"

if exist "C:\Users\madha\py\python.exe" (
    echo Launching with configured Python executable...
    "C:\Users\madha\py\python.exe" -m streamlit run app.py
    pause
    exit /b
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Launching with Python Launcher...
    py -m streamlit run app.py
    pause
    exit /b
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Launching with python...
    python -m streamlit run app.py
    pause
    exit /b
)

echo Python was not found!
pause
