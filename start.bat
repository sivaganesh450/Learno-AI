@echo off
echo ========================================
echo   LERNO - Student Learning Assistant
echo   Starting Application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Setting up Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing backend dependencies...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo [2/4] Starting Backend Server...
start "Lerno Backend" cmd /k "cd /d %cd% && venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000"

cd ..

echo.
echo [3/4] Setting up Frontend...
cd frontend

REM Install npm dependencies if node_modules doesn't exist
if not exist "node_modules\" (
    echo Installing frontend dependencies...
    call npm install
)

echo.
echo [4/4] Starting Frontend Server...
start "Lerno Frontend" cmd /k "cd /d %cd% && npm run dev"

cd ..

echo.
echo ========================================
echo   LERNO Started Successfully!
echo ========================================
echo.
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Frontend: http://localhost:5173
echo.
echo   Press Ctrl+C in each window to stop
echo ========================================
echo.

timeout /t 3 /nobreak >nul

REM Open browser after a delay
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo Application is running!
echo Close this window or press any key to exit...
pause >nul
