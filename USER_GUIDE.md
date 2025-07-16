# File Retention Refresher - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Operation Modes](#operation-modes)
5. [Configuration](#configuration)
6. [Usage Examples](#usage-examples)
7. [CSV Report Format](#csv-report-format)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Introduction

File Retention Refresher is a tool designed to help you freshen files that would otherwise be deleted based on retention rules.  This lets you keep important older files without all the manual work. It works by:

1. **Updating modification dates** to the current date/time for files older than 30 days
2. **Intelligently renaming files** to preserve their original dates in the filename
3. **Generating detailed reports** of all changes made

The tool features a retro Apple II-style interface and supports both bulk directory processing and targeted file processing via CSV input.

## Installation

### Windows (Build Executable)
```cmd
# Clone the repository
git clone https://github.com/rawneddy/files-refresher.git
cd files-refresher

# Build the executable
build_windows.bat

# Run the application (can double-click or use command prompt)
cd dist\win
file_refresher.exe
```

### Mac/Linux
```bash
# Clone the repository
git clone https://github.com/rawneddy/files-refresher.git
cd files-refresher

# Option 1: Run with Python (Recommended)
pip install -r requirements.txt
python3 file_refresher.py

# Option 2: Build executable (requires Python 3.10.2+)
./build_mac.sh
cd dist/mac
./file_refresher
```

**Note**: Mac executables must be run from terminal - double-clicking is not supported.

## Quick Start

### Basic Directory Processing
1. Run the application
2. Select **[D]irectory** mode
3. Enter the target directory path
4. Review the configuration
5. Choose **[P]rocess** to update files
6. Confirm to proceed
7. Check the generated CSV report

### Preview Mode (Dry Run)
1. Run the application
2. Select **[D]irectory** mode
3. Enter the target directory path
4. Review the configuration
5. Choose **[R]eport Only** to preview changes
6. Review the CSV report before actual processing

## Operation Modes

### Directory Mode
Processes all files in a directory and its subdirectories.

```
╔═══════════════════════════════════════════════════╗
║          FILE RETENTION REFRESHER v1.0            ║
║              [ APPLE ][ STYLE ]                   ║
╚═══════════════════════════════════════════════════╝

> SELECT MODE: [D]irectory or [C]SV Input? D
> SELECT DIRECTORY: /Users/documents/archive
> OPERATION TYPE: [P]rocess Files, [U]pdate Dates Only, or [R]eport Only? P
```

**Options:**
- **Process Files**: Makes actual changes to files (rename + date update)
- **Update Dates Only**: Updates modification dates without renaming
- **Report Only**: Generates CSV without making changes

### CSV Input Mode
Processes only specific files listed in a CSV file.

```
> SELECT MODE: [D]irectory or [C]SV Input? C
> CSV INPUT FILE: /Users/documents/files_to_process.csv
```

**CSV Requirements:**
- Must have columns: `new_path`, `original_modified`, `new_modified`, `extension`, `size_bytes`
- Use a report from a previous "Report Only" run
- Edit to include only files you want to process

## Configuration

Edit `config.yaml` to customize behavior:

### Adding File Extensions
```yaml
rename_extensions:
  # Default extensions
  - .docx
  - .xlsx
  - .pdf
  # Add your custom extensions
  - .dwg
  - .cad
  - .psd
```

### Changing the Age Threshold
```yaml
# Default: 30 days
days_threshold: 30
# Change to 60 days:
days_threshold: 60
```

### Report Settings
```yaml
report:
  # Change report naming pattern
  filename_pattern: "refresh_log_{date}.csv"
  # Save in a different location
  save_in_target_directory: false
  output_directory: "/Users/reports"
```

## Usage Examples

### Example 1: Archive Folder Maintenance
```bash
# Scenario: Refresh an old project archive
python file_refresher.py

# 1. Choose Directory mode
# 2. Enter: /Users/archives/project_2018
# 3. Choose Process Files
# 4. Confirm

# Result: All files updated, documents renamed:
# "Budget.xlsx" → "2018.03.15 Budget.xlsx"
# Modification dates set to today
```

### Example 2: Update Dates Only
```bash
# Scenario: Refresh dates without changing filenames
python file_refresher.py

# 1. Choose Directory mode
# 2. Enter: /Users/documents/reports
# 3. Choose Update Dates Only
# 4. Confirm

# Result: Only modification dates updated to today
# Original filenames preserved (no renaming)
```

### Example 3: Selective Processing
```bash
# Step 1: Generate a preview report
python file_refresher.py
# Choose Directory mode → Report Only

# Step 2: Edit the CSV to keep only .xlsx files

# Step 3: Process selected files
python file_refresher.py
# Choose CSV Input mode
# Select edited CSV file
```

### Example 4: Multiple Runs Safety
```bash
# First run:
"Presentation.pptx" → "2019.06.22 Presentation.pptx"

# Second run (same directory):
"2019.06.22 Presentation.pptx" → No change (already has date)

# Mixed format handling:
"2019-06-22 Report.docx" → "2019.06.22 Report.docx" (standardized)
```

## CSV Report Format

### Column Descriptions
- **new_path**: Full path after any renaming
- **original_modified**: Original file modification timestamp
- **new_modified**: Updated modification timestamp
- **extension**: File type without dot
- **size_bytes**: File size for verification

### Sample Report
```csv
new_path,original_modified,new_modified,extension,size_bytes
C:\Docs\2018.03.15 Budget Report.xlsx,2018-03-15 14:23:01,2025-07-11 09:15:32,xlsx,45678
C:\Docs\2019.06.22 Project Plan.docx,2019-06-22 09:11:45,2025-07-11 09:15:33,docx,123456
```

### Using Reports for Input
1. Open report in Excel/CSV editor
2. Delete rows for files to exclude
3. Save as CSV
4. Use as input for targeted processing

## Troubleshooting

### Common Issues

#### "Permission Denied" Errors
- Run as administrator (Windows)
- Check file ownership
- Close files in other applications

#### Files Not Being Renamed
- Check `config.yaml` for extension inclusion
- Verify file already has date prefix
- Ensure file matches age threshold

#### CSV Input Not Working
- Verify CSV format matches output format
- Check file paths are absolute
- Ensure no extra columns or headers

### Error Messages

#### "Directory not found"
- Use absolute paths (C:\Users\... or /Users/...)
- Check for typos
- Ensure directory exists

#### "Invalid CSV format"
- Column names must match exactly
- No extra spaces in headers
- Save as CSV, not Excel format

## Best Practices

### Before Running
1. **Backup important files** before first run
2. **Test on a small directory** first
3. **Use Report Only mode** to preview changes
4. **Review config.yaml** settings

### Recommended Workflow
1. Run in Report Only mode
2. Review the generated CSV
3. Edit CSV if selective processing needed
4. Run actual processing
5. Keep CSV reports for audit trail

### Safety Tips
- Tool never deletes files
- Original dates preserved in filename
- Can run multiple times safely
- Standardizes existing date formats

### Performance Tips
- Process smaller directories for faster results
- Close other applications accessing files
- Use CSV input mode for large directories with few target files

### Maintenance Schedule
- Run monthly on active archives
- Run quarterly on cold storage
- Keep CSV reports for compliance

## Testing and Development

### Generating Test Files
```bash
# Create test files for development/testing
python3 create_test_files.py

# This creates test_files/ directory with:
# - Microsoft Office files (.docx, .xlsx, .pptx)
# - Microsoft Visio files (.vsdx, .vsd) 
# - Files of various ages (5-500 days old)
# - Files with existing date prefixes
# - Files needing format conversion
# - Files that should not be renamed
```

### Resetting Test Environment
```bash
# Reset to clean state
rm -rf test_files
python3 create_test_files.py

# Verify clean state (should show 50 files)
ls -la test_files/
```

### Test Workflow
1. **Generate Test Files**: `python3 create_test_files.py`
2. **Test Dry Run**: `python3 file_refresher.py test_files --dry-run`
3. **Review Report**: Check generated CSV for expected changes
4. **Test Processing**: `python3 file_refresher.py test_files`
5. **Verify Results**: Check renamed files and updated dates
6. **Reset for Next Test**: `rm -rf test_files && python3 create_test_files.py`

### Testing Drag-and-Drop
1. Run application in interactive mode
2. When prompted for directory/CSV, drag file/folder into terminal
3. Press Enter to process the pasted path
4. Alternatively, type `browse` to open native file browser

## Advanced Usage

### Command Line Processing
```bash
# Direct directory processing
python3 file_refresher.py /path/to/directory

# Dry run mode
python3 file_refresher.py /path/to/directory --dry-run

# CSV input mode
python3 file_refresher.py --csv-input report.csv

# Non-interactive mode
python3 file_refresher.py /path/to/directory --no-ui
```

## Support

For issues or questions:
1. Check this user guide
2. Review error messages carefully
3. Verify configuration settings
4. Test with a small sample first

Remember: This tool is designed to preserve your files while satisfying retention policies. Always maintain backups of critical data.