#!/bin/bash

# SalaryPro - Startup Script for Linux/Mac
# This script starts the Flask application and opens it in your default browser

echo "╔═══════════════════════════════════════╗"
echo "║       SalaryPro - Starting Up         ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    PYTHON_CMD=".venv/bin/python"
    echo "✓ Virtual environment found"
else
    PYTHON_CMD="python3"
    echo "! Using system Python (virtual environment not found)"
fi

# Check if required packages are installed
echo "Checking dependencies..."
$PYTHON_CMD -c "import flask, pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    $PYTHON_CMD -m pip install flask pandas openpyxl
fi
echo "✓ Dependencies OK"

# URL to open
URL="http://127.0.0.1:5000"

# Function to open browser based on OS
open_browser() {
    sleep 2  # Wait for server to start
    if command -v xdg-open &> /dev/null; then
        xdg-open "$URL" 2>/dev/null
    elif command -v open &> /dev/null; then
        open "$URL"
    elif command -v gnome-open &> /dev/null; then
        gnome-open "$URL"
    else
        echo "Please open your browser and navigate to: $URL"
    fi
}

echo ""
echo "Starting SalaryPro server..."
echo "Opening browser at $URL"
echo ""
echo "Press Ctrl+C to stop the server"
echo "─────────────────────────────────────────"
echo ""

# Open browser in background
open_browser &

# Start the Flask application
$PYTHON_CMD app.py
