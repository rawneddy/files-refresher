#!/bin/bash

echo "=============================================="
echo "  FILE RETENTION REFRESHER - Mac/Linux Build"
echo "=============================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "[1/6] Creating virtual environment..."
rm -rf build_env
python3 -m venv build_env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/6] Activating virtual environment..."
source build_env/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "[3/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[4/6] Generating icon..."
python create_icon.py
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to generate icon, using default"
fi

echo "[5/6] Building executable with PyInstaller..."
pyinstaller --clean --noconfirm file_refresher.spec
if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller build failed"
    exit 1
fi

echo "[6/6] Packaging distribution..."
rm -rf file_refresher_mac
mkdir file_refresher_mac
cp dist/file_refresher file_refresher_mac/
cp config.yaml file_refresher_mac/
cp README.md file_refresher_mac/
cp USER_GUIDE.md file_refresher_mac/

# Make executable
chmod +x file_refresher_mac/file_refresher

echo
echo "=============================================="
echo "BUILD COMPLETE!"
echo "=============================================="
echo
echo "Executable created: file_refresher_mac/file_refresher"
echo
echo "Distribution package contents:"
echo "- file_refresher (main executable)"
echo "- config.yaml (configuration file)"
echo "- README.md (quick start guide)"
echo "- USER_GUIDE.md (detailed documentation)"
echo
echo "You can now distribute the 'file_refresher_mac' folder"
echo "or create a ZIP file for easy sharing."
echo