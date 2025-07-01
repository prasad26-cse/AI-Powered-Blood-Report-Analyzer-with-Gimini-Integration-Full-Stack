@echo off
echo Starting Optimized Blood Test Analyzer...
echo.

REM Check if we're in the right directory
if not exist "main_optimized.py" (
    echo Error: main_optimized.py not found in current directory
    echo Please run this script from the blood-test-analyser-debug directory
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "..\..\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "..\..\.venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found at ..\..\.venv
    echo Continuing with system Python...
)

REM Start the optimized server
echo Starting server...
python start_optimized.py

pause 