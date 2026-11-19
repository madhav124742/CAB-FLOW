@echo off
title CAB FLOW - REST API Server
echo ========================================================
echo        CAB FLOW - MACHINE LEARNING REST API
echo ========================================================
echo.
echo Starting Native Python API Server on port 8000...
echo Health endpoint: http://localhost:8000/api/health
echo Demand radar endpoint: http://localhost:8000/api/driver/demand-map
echo.
cd /d "%~dp0"
"C:\Users\madha\py\python.exe" api_server.py
pause

