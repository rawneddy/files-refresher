# Build Instructions - File Retention Refresher

## Overview
This document explains how to build standalone executables for Windows and Mac. Both platforms now have automated build scripts that handle the entire process.

## Prerequisites

### For Building on Windows
1. Python 3.10.2 or higher (required for PyInstaller compatibility)
2. Git (optional, for cloning repository)

### For Building on Mac
1. Python 3.10.2 or higher (required for PyInstaller compatibility)
2. Homebrew (recommended): `brew install python3`

## Building Windows Executable

### Automated Build (Recommended)

```cmd
# Clone the repository
git clone https://github.com/rawneddy/files-refresher.git
cd files-refresher

# Run the automated build script
build_windows.bat
```

The script will:
1. Check Python version compatibility
2. Create a clean virtual environment
3. Install all dependencies
4. Generate the application icon
5. Build the executable using PyInstaller
6. Package everything in `dist\windows\`

**Output**: `dist\windows\file_refresher.exe` with all necessary files

### Manual Build

```cmd
# Clone the repository
git clone https://github.com/rawneddy/files-refresher.git
cd files-refresher

# Create virtual environment
python -m venv build_env
build_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate icon
python create_icon.py

# Build executable
pyinstaller file_refresher.spec --noconfirm

# Package distribution
mkdir dist\windows
copy dist\file_refresher.exe dist\windows\
copy config.yaml dist\windows\
copy README.md dist\windows\
copy USER_GUIDE.md dist\windows\
```

## Building Mac Executable

### Automated Build (Recommended)

```bash
# Clone the repository
git clone https://github.com/rawneddy/files-refresher.git
cd files-refresher

# Run the automated build script
./build_mac.sh
```

The script will:
1. Check Python version compatibility (blocks 3.10.0 and 3.10.1)
2. Create a clean virtual environment
3. Install all dependencies
4. Generate the application icon
5. Build the executable using PyInstaller
6. Package everything in `dist/mac/`

**Output**: `dist/mac/file_refresher` with all necessary files

### Manual Build

```bash
# Clone the repository
git clone https://github.com/rawneddy/files-refresher.git
cd files-refresher

# Create virtual environment
python3 -m venv build_env
source build_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate icon
python create_icon.py

# Build executable
pyinstaller file_refresher.spec --noconfirm

# Package distribution
mkdir -p dist/mac
cp dist/file_refresher dist/mac/
cp config.yaml dist/mac/
cp README.md dist/mac/
cp USER_GUIDE.md dist/mac/
chmod +x dist/mac/file_refresher
```

## Running the Built Executables

### Windows
```cmd
cd dist\windows

# Option 1: Double-click file_refresher.exe in File Explorer
# Option 2: Run from command prompt
file_refresher.exe

# With arguments
file_refresher.exe --help
file_refresher.exe C:\path\to\directory --dry-run
```

### Mac
```bash
cd dist/mac

# Must run from terminal (double-click not supported)
./file_refresher

# With arguments
./file_refresher --help
./file_refresher /path/to/directory --dry-run
```

## Testing Your Build

### Generate Test Files
```bash
# Create sample files for testing
python3 create_test_files.py

# This creates test_files/ with:
# - Files of different ages (5-500 days old)
# - Various extensions (.docx, .xlsx, .pdf, .txt, etc.)
# - Files with existing date prefixes
# - Files needing format conversion
```

### Test the Application
```bash
# Test with the generated files
./dist/mac/file_refresher test_files --dry-run

# On Windows:
dist\windows\file_refresher.exe test_files --dry-run
```

## Troubleshooting

### Python Version Issues
**Error**: `Python 3.10.0 has a known PyInstaller compatibility issue`

**Solution**: 
```bash
# Upgrade Python using Homebrew (Mac)
brew install python3

# Or install specific version
brew install python@3.12
```

### Build Script Fails
1. **Check Python version**: Must be 3.10.2 or higher
2. **Clean previous builds**: Delete `build_env/`, `dist/`, `build/`
3. **Check permissions**: Ensure write access to project directory
4. **Internet connection**: Required for downloading dependencies

### Common PyInstaller Issues

**Missing modules**:
- Already handled in `file_refresher.spec` with `hiddenimports`

**Large executable size**:
- Normal for Python apps (includes interpreter)
- Current size: ~18MB

**Antivirus warnings**:
- Common with PyInstaller executables
- Add to antivirus whitelist if needed

### Performance
- **Build time**: 2-5 minutes depending on system
- **Executable size**: ~18MB (includes Python runtime)
- **Memory usage**: ~50MB when running

## Distribution

### Create Release Package

**Windows**:
```
file_refresher_windows_v1.0.zip
├── file_refresher.exe
├── config.yaml  
├── README.md
└── USER_GUIDE.md
```

**Mac**:
```
file_refresher_mac_v1.0.zip
├── file_refresher
├── config.yaml
├── README.md
└── USER_GUIDE.md
```

### File Structure After Build

```
project/
├── dist/
│   ├── windows/
│   │   ├── file_refresher.exe
│   │   ├── config.yaml
│   │   ├── README.md
│   │   └── USER_GUIDE.md
│   └── mac/
│       ├── file_refresher
│       ├── config.yaml
│       ├── README.md
│       └── USER_GUIDE.md
├── build/          (temporary files - can delete)
├── build_env/      (virtual environment - can delete)
└── file_refresher.spec
```

## Development Workflow

1. **Develop**: Edit source files
2. **Test**: `python3 file_refresher.py`
3. **Build**: Run build script
4. **Test Build**: Run executable with test files
5. **Package**: Create distribution ZIP
6. **Release**: Tag version and publish

For continuous development, you only need to rebuild when making releases.