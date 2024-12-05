@echo off
SETLOCAL EnableDelayedExpansion

REM Store original directory
SET "ORIGINAL_DIR=%CD%"

REM Set project root
SET "PROJECT_ROOT=C:\Users\irlen\Documents\projects\langchain\jarvis"

REM Verify projecz  t directory exists
IF NOT EXIST "%PROJECT_ROOT%" (
    echo Error: Project directory not found at %PROJECT_ROOT%
    exit /b 1
)

REM Get Poetry's virtual environment path
cd /d "%PROJECT_ROOT%"
FOR /F "tokens=* USEBACKQ" %%F IN (`poetry env info --path`) DO (
    SET "VENV_PATH=%%F"
)

REM Check if we got the venv path
IF NOT DEFINED VENV_PATH (
    echo Error: Could not find Poetry virtual environment
    cd /d "%ORIGINAL_DIR%"
    exit /b 1
)

REM Set PYTHONPATH
SET "PYTHONPATH=%PROJECT_ROOT%"

REM Activate venv and run
call "%VENV_PATH%\Scripts\activate.bat"

REM Return to original directory and run script
cd /d "%ORIGINAL_DIR%"
python "%PROJECT_ROOT%\jarvis\cli.py" %*

REM Store exit code
SET "SCRIPT_EXIT=%ERRORLEVEL%"

REM Deactivate venv
call "%VENV_PATH%\Scripts\deactivate.bat"

exit /b %SCRIPT_EXIT%