#!/bin/bash
# Create virtual environment
echo "Creating virtual environment..."
rm -rf venv
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r ../requirements.txt
