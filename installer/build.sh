#!/bin/bash

# Paths
SCRIPT="../main.py"
CONFIG_FILE="../config.json"
OUTPUT_NAME="dicom_waveform_extractor"

pip install pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "${OUTPUT_NAME}.spec"

# Run PyInstaller with single-file option and include config.json
echo "Building executable with PyInstaller..."
pyinstaller --onefile --clean --name "${OUTPUT_NAME}" --add-data "${CONFIG_FILE}:." "${SCRIPT}"

# Notify user of success
echo "Build complete. Executable is located in ./dist/${OUTPUT_NAME}"
