@echo off
title CAB FLOW - Complete System Launcher (Web + API)
echo ========================================================
echo         CAB FLOW - DUAL SERVER LAUNCHER
echo ========================================================
echo.
echo [1/2] Starting Native ML Inference API Server (Port 8000)...
start "CAB FLOW API" "C:\Users\madha\py\python.exe" api_server.py

echo [2/2] Starting Streamlit Interactive App (Port 8501)...
start "CAB FLOW Streamlit" "C:\Users\madha\py\python.exe" -m streamlit run app.py --server.port 8501

echo.
echo Opening Interactive Platform Dashboard in your browser...
start "" "http://localhost:8501"

echo ========================================================
echo Services Deployed Successfully!
echo - Streamlit App: http://localhost:8501
echo - ML API Engine: http://localhost:8000
echo ========================================================
echo.
pause

