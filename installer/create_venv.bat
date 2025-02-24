@echo off
echo Creating virtual environment...

REM Remove existing venv (if it exists)
IF EXIST venv rmdir /s /q venv

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r ..\requirements.txt

echo Virtual environment setup complete.
pause
