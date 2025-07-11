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
- **Language**: Python 3.9+
- **UI Framework**: Rich (for retro terminal interface)
- **Configuration**: YAML (PyYAML)
- **CSV Processing**: Python csv module
- **File Operations**: os, pathlib, shutil
- **Date/Time**: datetime
- **Packaging**: PyInstaller (for Windows executable)

### Project Structure
```
files-refresher/
├── file_refresher.py      # Main application
├── config.yaml            # User configuration
├── requirements.txt       # Python dependencies
├── README.md             # User documentation
├── PROJECT_DESIGN.md     # This file
├── CLAUDE.md            # AI context file
├── USER_GUIDE.md        # Detailed user guide
├── BUILD_INSTRUCTIONS.md # How to create executables
├── build_windows.bat    # Windows build script
├── file_refresher.spec  # PyInstaller configuration
└── dist/                # Windows executable output
```

## Feature Specifications

### 1. File Processing Logic

#### Renaming Rules
- **Target Extensions**: Defined in config.yaml (default: .docx, .xlsx, .pptx, .pdf, etc.)
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

#### Screen Flow
1. **Welcome Screen**
   - ASCII art logo
   - Version information
   - Retro Apple II green theme (#33FF33)

2. **Mode Selection**
   - [D]irectory or [C]SV Input

3. **Input Selection**
   - Directory: Path input with validation
   - CSV: File path input with format validation

4. **Configuration Review** (Directory mode only)
   - Display active extensions from config.yaml
   - Show modification threshold
   - Option to exit and modify config

5. **Operation Type** (Directory mode only)
   - [P]rocess Files
   - [R]eport Only

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
  # Documents
  - .pdf
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