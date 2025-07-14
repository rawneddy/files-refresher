@echo off
echo ===============================================
echo   FILE RETENTION REFRESHER - Windows Build
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
if exist build_env rmdir /s /q build_env
python -m venv build_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call build_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [3/6] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Generating icon...
python create_icon.py
if errorlevel 1 (
    echo WARNING: Failed to generate icon, using default
)

echo [5/6] Building executable with PyInstaller...
REM Clean PyInstaller build directories
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
pyinstaller --clean --noconfirm file_refresher.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo [6/6] Packaging distribution...
if exist dist\win rmdir /s /q dist\win
mkdir dist\win
copy dist\file_refresher.exe dist\win\
copy config.yaml dist\win\
copy README.md dist\win\
copy USER_GUIDE.md dist\win\

echo.
echo ===============================================
echo BUILD COMPLETE!
echo ===============================================
echo.
echo Executable created: dist\win\file_refresher.exe
echo.
echo Distribution package contents:
echo - file_refresher.exe (main executable)
echo - config.yaml (configuration file)
echo - README.md (quick start guide)
echo - USER_GUIDE.md (detailed documentation)
echo.
echo You can now distribute the 'dist\win' folder
echo or create a ZIP file for easy sharing.
echo.
pause