# File Retention Refresher - Project Design

## Overview
A cross-platform tool for updating file modification dates and intelligently renaming files with their original dates. Features a retro Apple II-style interface and flexible CSV-based workflows.

## Core Objectives
1. Update file modification dates to current datetime for files older than 30 days
2. Prepend original modification dates to filenames in `YYYY.MM.DD` format
3. Generate detailed CSV reports for audit trails
4. Support both directory scanning and targeted CSV input modes
5. Provide dry-run capability for preview before processing

## Technical Architecture

### Technology Stack
- **Language**: Python 3.10.2+ (PyInstaller compatibility requirement)
- **UI Framework**: Rich (for retro terminal interface)
- **Configuration**: YAML (PyYAML)
- **CSV Processing**: Python csv module
- **File Operations**: os, pathlib, shutil
- **Date/Time**: datetime
- **Packaging**: PyInstaller (for Windows and Mac executables)
- **Icon Generation**: Pillow (for .ico creation)

### Project Structure
```
files-refresher/
├── file_refresher.py      # Main application
├── config.yaml            # User configuration
├── requirements.txt       # Python dependencies
├── create_test_files.py   # Test file generator
├── create_icon.py        # Icon generation script
├── file_refresher.spec   # PyInstaller configuration
├── build_windows.bat     # Windows build script
├── build_mac.sh          # Mac build script
├── icon.ico              # Application icon (generated)
├── icon.png              # Icon preview (generated)
├── README.md             # User documentation
├── PROJECT_DESIGN.md     # This file
├── CLAUDE.md             # AI context file
├── USER_GUIDE.md         # Detailed user guide
├── BUILD_INSTRUCTIONS.md # How to create executables
├── .gitignore            # Git ignore patterns
├── dist/                 # Build outputs (gitignored)
│   ├── windows/          # Windows executable + files
│   └── mac/              # Mac executable + files
├── build/                # PyInstaller temp files (gitignored)
├── build_env/            # Virtual environment (gitignored)
└── test_files/           # Generated test files (gitignored)
```

## Feature Specifications

### 1. File Processing Logic

#### Renaming Rules
- **Target Extensions**: Defined in config.yaml (default: .docx, .doc, .xlsx, .xls, .pptx, .ppt, .vsdx, .vsd)
- **Excluded Extensions**: CSV files are automatically excluded from processing
- **Date Detection Patterns**:
  - No date → Add `YYYY.MM.DD` prefix using original modified date
  - `YYYY-MM-DD` prefix → Convert to `YYYY.MM.DD`
  - `YYYY.MM.DD` prefix → No change needed
- **Format**: `YYYY.MM.DD OriginalFilename.ext`

#### Modification Date Update
- **Threshold**: Files older than 30 days (configurable)
- **Scope**: ALL files, regardless of extension
- **New Date**: Current system datetime

### 2. Operation Modes

#### Directory Mode
- **Input**: Target directory path
- **Options**:
  - Process Files: Execute renaming and date updates
  - Report Only: Generate CSV without making changes (dry run)
- **Recursive**: Processes all subdirectories

#### CSV Input Mode
- **Input**: CSV file with specific file list
- **Format**: Must match output CSV format
- **Use Case**: Precise control over which files to process
- **Validation**: Checks file existence before processing

### 3. User Interface Design

#### Screen Flow (Updated)
1. **Welcome Screen**
   - ASCII art logo
   - Version information
   - Retro Apple II green theme (#33FF33)

2. **Configuration Review** (Step 1 of 4)
   - Display active extensions from config.yaml
   - Show modification threshold
   - Option to exit and modify config

3. **Mode Selection** (Step 2 of 4)
   - [D]irectory or [C]SV Input
   - Clear screen between steps

4. **Input Selection** (Step 3 of 4)
   - Directory: Path input with validation, drag-and-drop, file browser
   - CSV: File path input with validation, drag-and-drop, file browser

5. **Operation Type** (Step 4 of 4, Directory mode only)
   - [P]rocess Files
   - [R]eport Only
   - Shows selected path at top of screen

6. **Pre-scan Summary**
   - File type breakdown
   - Count of files to be modified
   - Count of files already processed
   - Total size estimation

7. **Confirmation Prompt**
   - Clear summary of actions
   - Y/N confirmation

8. **Progress Display**
   - ASCII progress bar
   - Current file being processed
   - Completion percentage
   - Estimated time remaining

9. **Completion Summary**
   - Files processed
   - Files renamed
   - Dates updated
   - CSV report location

#### Visual Style
```
╔═══════════════════════════════════════════════════╗
║          FILE RETENTION REFRESHER v1.0            ║
║              [ APPLE ][ STYLE ]                   ║
╚═══════════════════════════════════════════════════╝

> PROCESSING FILES...

[████████████████████░░░░░░░░░░░░░░░░░░░] 52%
Currently: 2018.03.15 Budget Report.xlsx
Files Processed: 267 / 512
Time Remaining: ~2 minutes
```

### 4. CSV Report Format

#### Columns
1. **new_path**: Full absolute path after any renaming
2. **original_modified**: Original modification timestamp (YYYY-MM-DD HH:MM:SS)
3. **new_modified**: Updated modification timestamp (YYYY-MM-DD HH:MM:SS)
4. **extension**: File extension without dot (e.g., "xlsx", "pdf")
5. **size_bytes**: File size in bytes

#### Example
```csv
new_path,original_modified,new_modified,extension,size_bytes
/Users/docs/2018.03.15 Budget Report.xlsx,2018-03-15 14:23:01,2025-07-11 09:15:32,xlsx,45678
/Users/docs/2019.06.22 Presentation.pptx,2019-06-22 09:11:45,2025-07-11 09:15:33,pptx,234567
```

### 5. Configuration File (config.yaml)

```yaml
# File Retention Refresher Configuration

# Extensions to rename (add date prefix)
rename_extensions:
  # Microsoft Office
  - .docx
  - .doc
  - .xlsx
  - .xls
  - .pptx
  - .ppt
  # Microsoft Visio
  - .vsdx
  - .vsd
  # Add custom extensions below
  # - .dwg
  # - .txt

# Update modification date for files older than this many days
days_threshold: 30

# Report settings
report:
  # {date} will be replaced with YYYY.MM.DD
  filename_pattern: "file_refresh_report_{date}.csv"
  # Save report in same directory as processed files
  save_in_target_directory: true

# UI settings
ui:
  # Retro color theme
  primary_color: "#33FF33"
  # Show detailed file info during processing
  verbose_progress: true
```

## Implementation Plan

### Phase 1: Core Functionality
1. File system operations module
2. Date detection and formatting logic
3. CSV report generation
4. Basic CLI interface

### Phase 2: User Interface
1. Rich-based retro UI implementation
2. Progress tracking system
3. Interactive wizard flow
4. Error handling displays

### Phase 3: Advanced Features
1. CSV input mode
2. Dry-run capability
3. Configuration management
4. Input validation

### Phase 4: Packaging & Testing
1. PyInstaller configuration
2. Cross-platform testing
3. Error handling improvements
4. Performance optimization

## Error Handling

### File Access Errors
- Permission denied: Log and skip file
- File locked: Retry with timeout
- Path too long: Log with truncated display

### Data Validation
- Invalid directory: Prompt for correction
- Malformed CSV: Show specific error location
- Invalid date formats: Use fallback logic

### Recovery Options
- Auto-save progress for resume capability
- Partial completion reports
- Rollback option for renamed files

## Performance Considerations

### Large Directory Handling
- Batch processing (100 files at a time)
- Memory-efficient file scanning
- Progress checkpoint saves

### Optimization Strategies
- Pre-compile regex patterns
- Cached file type detection
- Parallel processing for scanning (not modification)

## Security Considerations

### File Safety
- No deletion operations
- Original filename preserved in new name
- Detailed audit trail via CSV

### Path Validation
- Prevent directory traversal
- Validate absolute paths only
- Check write permissions before starting

## Testing Framework

### Test File Generation
```bash
# Generate fresh test files
python3 create_test_files.py

# This creates test_files/ directory with:
# - Office documents (.docx, .xlsx, .pptx)
# - Visio diagrams (.vsdx, .vsd) 
# - Files with various ages (5-500 days old)
# - Files with existing date prefixes (YYYY.MM.DD format)
# - Files needing conversion (YYYY-MM-DD format)
# - Files that should not be renamed (.txt, .png, .csv)
```

### Test Environment Reset
```bash
# Clean slate for testing
rm -rf test_files
python3 create_test_files.py

# Verify clean state
ls -la test_files/  # Should show 13 original files
```

### Test Scenarios
1. **Fresh Directory Processing**: Use clean test_files with mixed file types
2. **CSV Report Generation**: Test dry-run mode for report creation
3. **CSV Input Processing**: Use generated reports as input for selective processing
4. **Drag-and-Drop Testing**: Test path input via drag-and-drop functionality
5. **Error Handling**: Test with invalid paths, locked files, permission issues

## Future Enhancements

### Potential Features
1. Network drive support
2. Cloud storage integration
3. Scheduled/automated runs
4. Multi-threaded processing
5. Undo functionality
6. Regular expression filename patterns
7. Email report delivery
8. GUI version alongside CLI