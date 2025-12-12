@echo off
REM SalaryPro - Startup Script for Windows
REM This script starts the Flask application and opens it in your default browser

title SalaryPro - Salary Management System

echo ========================================
echo        SalaryPro - Starting Up
echo ========================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    set PYTHON_CMD=.venv\Scripts\python.exe
    echo [OK] Virtual environment found
) else (
    set PYTHON_CMD=python
    echo [!] Using system Python (virtual environment not found)
)

REM Check if required packages are installed
echo Checking dependencies...
%PYTHON_CMD% -c "import flask, pandas, openpyxl" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    %PYTHON_CMD% -m pip install flask pandas openpyxl
)
echo [OK] Dependencies OK

echo.
echo Starting SalaryPro server...
echo Opening browser at http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo ----------------------------------------
echo.

REM Open browser after a short delay (using start with timeout)
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

REM Start the Flask application
%PYTHON_CMD% app.py

pause
