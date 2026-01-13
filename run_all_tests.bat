@echo off
REM Master test runner for Windows - runs all tests

echo ==========================================
echo Running All Tests (Backend + Worker + Frontend)
echo ==========================================

set FAILED=0

REM Run backend tests
echo.
echo 1/3 Backend Tests...
cd backend
call run_tests.bat
if %ERRORLEVEL% NEQ 0 set FAILED=1
cd ..

REM Run worker tests
echo.
echo 2/3 Worker Tests...
cd worker
call run_tests.bat
if %ERRORLEVEL% NEQ 0 set FAILED=1
cd ..

REM Run frontend tests
echo.
echo 3/3 Frontend Tests...
cd frontend
call npm test -- --run
if %ERRORLEVEL% NEQ 0 set FAILED=1
cd ..

REM Final result
echo.
echo ==========================================
if %FAILED% EQU 0 (
    echo ✅ All test suites passed!
) else (
    echo ❌ Some test suites failed!
    exit /b 1
)
echo ==========================================
