@echo off
setlocal EnableExtensions

rem Daily PM Decision apply job (invoked by Task Scheduler).
set "PROJECT_ROOT=%~dp0.."
set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
set "LOG_DIR=%LOCALAPPDATA%\pm-decision\logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "LOG_DATE=%%I"
set "LOG_FILE=%LOG_DIR%\daily-%LOG_DATE%.log"

cd /d "%PROJECT_ROOT%"
echo ===== %DATE% %TIME% =====>> "%LOG_FILE%"
"%PYTHON_EXE%" -m pm_decision --apply >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"
echo Exit code: %EXIT_CODE%>> "%LOG_FILE%"
exit /b %EXIT_CODE%
