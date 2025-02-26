@echo off

REM Clear the screen
cls

echo ============================================
echo Cleaning Previous Builds
echo ============================================

REM Define paths
set SCRIPT=..\main.py
set CONFIG_FILE=..\config.json
set OUTPUT_NAME=dicom_waveform_extractor

REM Step 1: Remove old build files
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %OUTPUT_NAME%.spec del %OUTPUT_NAME%.spec

REM Step 2: Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Step 3: Ensure PyInstaller is installed in the virtual environment
echo Checking PyInstaller installation...
venv\Scripts\python -m pip show pyinstaller >nul 2>&1 || (
    echo Installing PyInstaller...
    venv\Scripts\python -m pip install pyinstaller || (
        echo Failed to install PyInstaller. Exiting...
        exit /b 1
    )
)

REM Step 4: Build Executable with PyInstaller
echo Building executable with PyInstaller...
venv\Scripts\python -m pyinstaller --onefile --clean ^
--name "%OUTPUT_NAME%" ^
--add-data "%CONFIG_FILE%;." ^
--hidden-import gdcm ^
--hidden-import jinja2 ^
--hidden-import PIL ^
--hidden-import tqdm ^
--hidden-import simplejson ^
--hidden-import pkg_resources.extern ^
"%SCRIPT%"

REM Step 5: Notify user of build completion
echo ============================================
echo Build complete. Executable is located in .\dist\%OUTPUT_NAME%.
echo ============================================

pause