# Build Instructions - File Retention Refresher

## Overview
This document explains how to build standalone executables for Windows and optionally for Mac. The Windows executable allows users to run the application without installing Python.

## Prerequisites

### For Building on Windows
1. Python 3.9 or higher installed
2. Git (optional, for cloning repository)

### For Building on Mac (for Windows)
1. Python 3.9 or higher installed
2. Wine or a Windows VM (for true Windows executable)
3. OR use GitHub Actions (recommended for cross-platform builds)

## Building Windows Executable

### Method 1: Direct Build on Windows

1. **Clone or download the repository**
   ```cmd
   git clone [repository-url]
   cd files-refresher
   ```

2. **Create virtual environment** (recommended)
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

4. **Build the executable**
   ```cmd
   pyinstaller --onefile --name file_refresher --icon=icon.ico file_refresher.py
   ```
   
   Or use the spec file (if provided):
   ```cmd
   pyinstaller file_refresher.spec
   ```

5. **Find your executable**
   - Location: `dist/file_refresher.exe`
   - Copy `config.yaml` to the same directory as the .exe

### Method 2: Using Build Script

Create `build_windows.bat`:
```batch
@echo off
echo Building File Retention Refresher for Windows...

REM Create virtual environment
python -m venv build_env
call build_env\Scripts\activate

REM Install dependencies
pip install -r requirements.txt
pip install pyinstaller

REM Build executable
pyinstaller --onefile ^
    --name file_refresher ^
    --add-data "config.yaml;." ^
    --distpath ./dist ^
    --workpath ./build ^
    --specpath ./build ^
    --noconfirm ^
    --clean ^
    file_refresher.py

echo.
echo Build complete! Executable located in: dist\file_refresher.exe
pause
```

Then simply run:
```cmd
build_windows.bat
```

## Building from Mac (Cross-Platform)

### Method 1: Using GitHub Actions (Recommended)

Create `.github/workflows/build.yml`:
```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --onefile --name file_refresher file_refresher.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: windows-executable
        path: dist/file_refresher.exe

  build-mac:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --onefile --name file_refresher file_refresher.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: mac-executable
        path: dist/file_refresher
```

### Method 2: Local Mac Build (Mac executable only)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Build Mac executable**
   ```bash
   pyinstaller --onefile --name file_refresher file_refresher.py
   ```

3. **Make it executable**
   ```bash
   chmod +x dist/file_refresher
   ```

## PyInstaller Specification File

Create `file_refresher.spec` for more control:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['file_refresher.py'],
    pathex=[],
    binaries=[],
    datas=[('config.yaml', '.')],
    hiddenimports=['rich', 'yaml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='file_refresher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

## Development Workflow

### For Developers on Mac

1. **Develop and test on Mac**
   ```bash
   python file_refresher.py
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Feature update"
   git push
   ```

3. **Create release tag** (triggers build)
   ```bash
   git tag v1.0.0
   git push --tags
   ```

4. **Download Windows executable** from GitHub Actions artifacts

### For End Users

#### Windows Users
1. Download `file_refresher.exe` from releases
2. Download `config.yaml` 
3. Place both in same directory
4. Double-click exe or run from command prompt

#### Mac/Linux Users
```bash
# No build needed - run directly
python file_refresher.py
```

## Troubleshooting

### Common Build Issues

1. **"Module not found" errors**
   - Add to hiddenimports in .spec file
   - Example: `hiddenimports=['rich', 'yaml', 'csv']`

2. **Antivirus warnings**
   - Common with PyInstaller
   - Sign the executable or add to whitelist

3. **Large executable size**
   - Normal for Python executables (includes interpreter)
   - Use UPX compression: `--upx-dir=/path/to/upx`

4. **Config file not found**
   - Use `--add-data` flag to bundle
   - Or document that users need to copy it manually

### Testing the Executable

1. **Test on clean Windows system**
   - No Python installed
   - Different Windows versions

2. **Test all features**
   - Directory mode
   - CSV mode
   - Config file reading
   - Report generation

## Distribution Package

Create a release package:
```
file_refresher_v1.0.0_windows.zip
├── file_refresher.exe
├── config.yaml
├── README.txt
└── sample_report.csv
```

## Alternative: Python Embedded Distribution

For users who prefer not to use executables:

1. Download Python embedded distribution
2. Extract to folder
3. Add packages: `python.exe -m pip install rich pyyaml`
4. Create batch file to run:
   ```batch
   @echo off
   python.exe file_refresher.py %*
   ```

This provides a portable Python environment without system installation.