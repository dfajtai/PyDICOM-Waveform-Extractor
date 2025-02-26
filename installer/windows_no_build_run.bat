@echo off

REM Clear the screen
cls

echo ============================================
echo Setting up Python Virtual Environment
echo ============================================

REM Define variables
set VENV_DIR=venv
set PYTHON_VERSION=3.13
set REQUIREMENTS_FILE=..\requirements.txt
set SCRIPT_TO_RUN=..\main.py

REM Step 1: Check if the specified Python version is available
py -%PYTHON_VERSION% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python %PYTHON_VERSION% is not installed or not available via the py launcher.
    echo Please install Python %PYTHON_VERSION% from https://www.python.org/downloads/.
    exit /b 1
)

REM Step 2: Create Virtual Environment if it doesn't exist
if not exist %VENV_DIR% (
    echo Creating virtual environment using Python %PYTHON_VERSION%...
    py -%PYTHON_VERSION% -m venv %VENV_DIR%
) else (
    echo Virtual environment already exists.
)

REM Step 3: Activate Virtual Environment
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat

REM Step 4: Upgrade pip in the Virtual Environment
echo Upgrading pip...
python -m pip install --upgrade pip

REM Step 5: Install Dependencies from requirements.txt (if present)
if exist %REQUIREMENTS_FILE% (
    echo Installing dependencies from %REQUIREMENTS_FILE%...
    python -m pip install -r %REQUIREMENTS_FILE%
) else (
    echo WARNING: %REQUIREMENTS_FILE% not found. Skipping dependency installation.
)

REM Step 6: Run the Python Script
if exist %SCRIPT_TO_RUN% (
    echo ============================================
    echo Running Python script: %SCRIPT_TO_RUN%...
    where python
    python --version
    python %SCRIPT_TO_RUN%
) else (
    echo ERROR: Python script %SCRIPT_TO_RUN% not found!
)

REM Step 7: Deactivate Virtual Environment
echo Deactivating virtual environment...
deactivate

echo ============================================
echo Script execution complete.
echo ============================================
pause
