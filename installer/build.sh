#!/bin/bash

# Ensure the script stops on errors
set -e

# Paths
SCRIPT="../main.py"
CONFIG_FILE="../config.json"
OUTPUT_NAME="dicom_waveform_extractor"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r ../requirements.txt

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "${OUTPUT_NAME}.spec"

# Run PyInstaller with single-file option and include config.json
echo "Building executable with PyInstaller..."
pyinstaller --onefile --clean --name "${OUTPUT_NAME}" --add-data "${CONFIG_FILE}:." "${SCRIPT}"

# Notify user of success
echo "Build complete. Executable is located in ./dist/${OUTPUT_NAME}"