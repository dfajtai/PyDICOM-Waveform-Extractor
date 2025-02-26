@echo off
echo Cleaning previous builds...

REM Define paths
set SCRIPT=..\main.py
set CONFIG_FILE=..\config.json
set OUTPUT_NAME=dicom_waveform_extractor.exe

REM Remove old build files
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del %OUTPUT_NAME%.spec 2>nul

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Building executable with PyInstaller...
venv\Scripts\python -m pyinstaller --onefile --clean --name "%OUTPUT_NAME%" --add-data "%CONFIG_FILE%;." "%SCRIPT%"

echo Build complete. Executable is located in .\dist\%OUTPUT_NAME%
pause
