# File Retention Refresher

A Python application designed to bypass file retention policies by updating modification dates and intelligently renaming files with their original dates. Features a retro Apple II-style terminal interface.

## 🚀 Quick Start

### Windows Users
```bash
# Clone the repository
git clone https://github.com/rawneddy/files-refresher.git
cd files-refresher

# Build Windows executable
build_windows.bat

# Run the executable (can double-click or use command prompt)
cd dist\windows
file_refresher.exe
```

### Mac/Linux Users
```bash
# Clone the repository
git clone https://github.com/rawneddy/files-refresher.git
cd files-refresher

# Option 1: Run directly with Python (Recommended)
pip install -r requirements.txt
python3 file_refresher.py

# Option 2: Build executable (if PyInstaller compatible)
./build_mac.sh

# Run the executable (terminal required)
cd dist/mac
./file_refresher
```

> **Note**: Some macOS systems may have PyInstaller compatibility issues. If the build fails, use Option 1 to run directly with Python.

> **Note**: Pre-built releases will be available in the future. For now, please build locally using the instructions above.

## ✨ Features

- **🔄 File Date Refresh**: Updates modification dates to bypass retention policies
- **📅 Smart Renaming**: Preserves original dates in filenames (YYYY.MM.DD format)
- **🖥️ Retro UI**: Apple II-style green terminal interface
- **📊 CSV Reporting**: Detailed audit trails with versioned reports
- **🎯 Selective Processing**: Process specific files via CSV input
- **🔍 Dry-Run Mode**: Preview changes before making them
- **⚙️ Configurable**: YAML configuration for file extensions and settings

## 🎮 Interface Preview

```
╔═══════════════════════════════════════════════════╗
║          FILE RETENTION REFRESHER v1.0            ║
║              [ APPLE ][ STYLE ]                   ║
╚═══════════════════════════════════════════════════╝

> SELECT MODE [D/C]: D
> SELECT DIRECTORY: /Users/documents/archive
> OPERATION TYPE [P/R]: P

PROCESSING FILES...
[████████████████████░░░░░░░░░░░░░░░░░░░] 75%
Currently: 2018.03.15 Budget Report.xlsx
```

## 🔧 Usage Modes

### Interactive Mode (Recommended)
```bash
python3 file_refresher.py
```
- Guided wizard interface
- Mode selection (Directory/CSV)
- Operation type selection (Process/Report Only)
- Real-time progress tracking

### Command Line Mode
```bash
# Process directory
python3 file_refresher.py /path/to/directory

# Dry run (preview only)
python3 file_refresher.py /path/to/directory --dry-run

# Process specific files from CSV
python3 file_refresher.py --csv-input report.csv

# Non-interactive mode
python3 file_refresher.py /path/to/directory --no-ui
```

## 📋 Workflow Examples

### Basic File Refresh
1. Run: `python3 file_refresher.py`
2. Choose Directory mode
3. Select your target folder
4. Choose "Process Files"
5. Confirm settings and proceed

### Selective Processing
1. Run with "Report Only" to generate CSV
2. Edit CSV to keep only desired files
3. Run with CSV input mode using edited file
4. Review results

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# File extensions to rename
rename_extensions:
  - .docx
  - .xlsx
  - .pdf
  # Add your custom extensions

# Age threshold for date updates
days_threshold: 30

# Report settings
report:
  filename_pattern: "file_refresh_report_{date}.csv"
```

## 📊 CSV Reports

Every run generates a detailed CSV report with:
- `new_path`: Full path after any renaming
- `original_modified`: Original modification timestamp
- `new_modified`: Updated modification timestamp
- `extension`: File extension for filtering
- `size_bytes`: File size for verification

Reports use versioned naming: `report_2025.07.11.csv`, `report_2025.07.11.01.csv`, etc.

## 🛡️ Safety Features

- **No File Deletion**: Never removes files, only renames and updates dates
- **Comprehensive Logging**: All operations logged to `file_refresher.log`
- **Error Handling**: Graceful handling of permission issues and locked files
- **Dry-Run Mode**: Preview all changes before execution
- **Audit Trail**: Complete CSV reports for compliance

## 🔨 Building Executables

### Automated Build (Recommended)
```bash
# Windows
build_windows.bat

# Mac/Linux  
./build_mac.sh
```

### Manual Build
```bash
# Install PyInstaller
pip install pyinstaller

# Generate icon
python create_icon.py

# Build with PyInstaller
pyinstaller file_refresher.spec
```

### Development Mode
```bash
# Run directly without building
pip install -r requirements.txt
python3 file_refresher.py
```

### Testing
```bash
# Generate test files for development/testing
python3 create_test_files.py

# This creates a test_files/ directory with:
# - Files of different ages (5-500 days old)
# - Various file types (.docx, .xlsx, .pdf, .txt, .csv, .png)
# - Files with existing date prefixes (2019.06.15 format)
# - Files needing date conversion (YYYY-MM-DD to YYYY.MM.DD)
# - Recent files that shouldn't be modified

# Test the application with generated files
python3 file_refresher.py test_files --dry-run
```

## 📚 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)**: Comprehensive user manual
- **[PROJECT_DESIGN.md](PROJECT_DESIGN.md)**: Technical specifications
- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)**: Executable creation guide

## 🐛 Troubleshooting

### Common Issues

**Permission Denied Errors**
- Run as administrator (Windows) or with sudo (Mac/Linux)
- Check file ownership and permissions

**Files Not Being Renamed**
- Verify file extensions in `config.yaml`
- Ensure files meet age threshold criteria

**CSV Input Not Working**
- Check CSV format matches output format exactly
- Verify file paths are absolute

**PyInstaller Build Fails on Mac**
- This is a known compatibility issue with Python 3.10.0 and 3.10.1
- Solution: Upgrade to Python 3.10.2+ using: `brew install python3`
- Workaround: Run directly with Python: `pip install -r requirements.txt && python3 file_refresher.py`

### Getting Help
1. Check the error messages and log file
2. Review the [USER_GUIDE.md](USER_GUIDE.md)
3. Ensure all dependencies are installed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**⚠️ Important**: This tool modifies file metadata. Always maintain backups of critical data before use.