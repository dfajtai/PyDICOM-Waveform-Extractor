@echo off

REM Paths
set SCRIPT=..\main.py
set CONFIG_FILE=..\config.json
set OUTPUT_NAME=dicom_waveform_extractor

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r ..\requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
rmdir /s /q build dist %OUTPUT_NAME%.spec

REM Build executable with PyInstaller
echo Building executable with PyInstaller...
pyinstaller --onefile --clean --name "%OUTPUT_NAME%" --add-data "%CONFIG_FILE%;." "%SCRIPT%"

REM Notify user of success
echo Build complete. Executable is located in .\dist\%OUTPUT_NAME%
pause
