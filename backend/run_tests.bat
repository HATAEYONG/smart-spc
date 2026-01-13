@echo off
REM Backend test runner script for Windows

echo ===================================
echo Running Backend Tests (pytest)
echo ===================================

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run pytest with coverage
pytest --cov=apps --cov-report=html --cov-report=term-missing -v

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ All tests passed!
    echo 📊 Coverage report: backend\htmlcov\index.html
) else (
    echo.
    echo ❌ Some tests failed!
    exit /b 1
)
