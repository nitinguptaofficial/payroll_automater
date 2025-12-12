# SalaryPro - Startup Script for Windows PowerShell
# This script starts the Flask application and opens it in your default browser

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       SalaryPro - Starting Up         " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists
if (Test-Path ".venv\Scripts\python.exe") {
    $PythonCmd = ".venv\Scripts\python.exe"
    Write-Host "[OK] Virtual environment found" -ForegroundColor Green
} else {
    $PythonCmd = "python"
    Write-Host "[!] Using system Python (virtual environment not found)" -ForegroundColor Yellow
}

# Check if required packages are installed
Write-Host "Checking dependencies..."
& $PythonCmd -c "import flask, pandas, openpyxl" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    & $PythonCmd -m pip install flask pandas openpyxl
}
Write-Host "[OK] Dependencies OK" -ForegroundColor Green

$URL = "http://127.0.0.1:5000"

Write-Host ""
Write-Host "Starting SalaryPro server..." -ForegroundColor Cyan
Write-Host "Opening browser at $URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "----------------------------------------"
Write-Host ""

# Open browser after a delay in background
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process $using:URL
} | Out-Null

# Start the Flask application
& $PythonCmd app.py
