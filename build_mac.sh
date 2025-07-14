#!/bin/bash

echo "=============================================="
echo "  FILE RETENTION REFRESHER - Mac/Linux Build"
echo "=============================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10.2 or higher"
    exit 1
fi

# Check Python version for PyInstaller compatibility
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Found Python $PYTHON_VERSION"

# Function to compare version numbers
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Check if Python version is >= 3.10.2 (fixes PyInstaller bug)
if version_ge "$PYTHON_VERSION" "3.10.2"; then
    echo "✓ Python version is compatible with PyInstaller"
elif [[ "$PYTHON_VERSION" == "3.10.0" ]] || [[ "$PYTHON_VERSION" == "3.10.1" ]]; then
    echo "ERROR: Python $PYTHON_VERSION has a known PyInstaller compatibility issue"
    echo "Please upgrade to Python 3.10.2 or higher to fix this bug"
    echo ""
    echo "Options:"
    echo "1. Install newer Python: brew install python@3.12"
    echo "2. Use Python directly: pip install -r requirements.txt && python3 file_refresher.py"
    exit 1
elif version_ge "3.10.0" "$PYTHON_VERSION"; then
    echo "WARNING: Python $PYTHON_VERSION is older than recommended"
    echo "Consider upgrading to Python 3.10.2+ for best PyInstaller compatibility"
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
echo "Cleaning previous build artifacts..."
rm -rf build
rm -rf dist
echo "Building with spec file configuration..."
pyinstaller --clean --noconfirm file_refresher.spec

if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller build failed"
    echo "This appears to be a PyInstaller compatibility issue with your Python version."
    echo ""
    echo "WORKAROUND: You can run the application directly with Python:"
    echo "1. Install dependencies: pip install -r requirements.txt"
    echo "2. Run the app: python3 file_refresher.py"
    echo ""
    echo "Testing if the Python script works directly..."
    echo ""
    
    # Test if the script runs without PyInstaller
    cd /
    cd "$OLDPWD"
    source build_env/bin/activate
    python3 file_refresher.py --help
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Good news! The Python script works correctly."
        echo "✓ You can use it directly without building an executable."
        echo ""
        echo "To run the application:"
        echo "  cd $(pwd)"
        echo "  source build_env/bin/activate"
        echo "  python3 file_refresher.py"
    else
        echo ""
        echo "✗ The Python script also has issues. Please check dependencies."
    fi
    
    exit 1
fi

echo "[6/6] Packaging distribution..."
rm -rf dist/mac
mkdir -p dist/mac
cp dist/file_refresher dist/mac/
cp config.yaml dist/mac/
cp README.md dist/mac/
cp USER_GUIDE.md dist/mac/

# Make executable
chmod +x dist/mac/file_refresher

echo
echo "=============================================="
echo "BUILD COMPLETE!"
echo "=============================================="
echo
echo "Executable created: dist/mac/file_refresher"
echo
echo "Distribution package contents:"
echo "- file_refresher (main executable)"
echo "- config.yaml (configuration file)"
echo "- README.md (quick start guide)"
echo "- USER_GUIDE.md (detailed documentation)"
echo
echo "You can now distribute the 'dist/mac' folder"
echo "or create a ZIP file for easy sharing."
echo