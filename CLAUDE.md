# CLAUDE.md - AI Context for File Retention Refresher

## Project Overview
This is a Python application designed to help keep files fresh by updating modification dates and intelligently renaming files. It features a retro Apple II-style terminal interface and supports both bulk and targeted file processing.

## Key Requirements

### Core Functionality
1. **Two Main Operations**:
   - Update file modification dates to current datetime (for ALL files > 30 days old)
   - Rename files by prepending original date as `YYYY.MM.DD` (only for configured extensions)

2. **Processing Order**:
   - First: Check if file needs renaming (extension match + date logic)
   - Second: Update modification date if > 30 days old

3. **Date Format Rules**:
   - Standard format: `YYYY.MM.DD` (dots, not hyphens)
   - No date → Add `YYYY.MM.DD OriginalName.ext`
   - Has `YYYY-MM-DD` → Convert to `YYYY.MM.DD`
   - Has `YYYY.MM.DD` → No change

### User Interface
- Retro Apple II green terminal style using Rich library
- Color: #33FF33 (classic green phosphor)
- ASCII art borders and progress bars
- Linear wizard flow with clear prompts

### Operation Modes
1. **Directory Mode**:
   - Process all files in directory (recursive)
   - Two sub-modes: Process Files or Report Only (dry run)

2. **CSV Input Mode**:
   - Process only files listed in input CSV
   - Uses same format as output reports

### Configuration
- YAML file for settings
- Customizable file extensions for renaming
- Configurable age threshold (default 30 days)

### CSV Report Format
Columns: `new_path`, `original_modified`, `new_modified`, `extension`, `size_bytes`

## Technical Decisions

### Libraries
- **Rich**: For retro terminal UI (chosen over Textual for simplicity)
- **PyYAML**: Configuration management
- **pathlib**: Modern path handling
- **PyInstaller**: Windows executable packaging

### Important Behaviors
1. Never delete files
2. Preserve original information in filename
3. Handle multiple runs safely (idempotent)
4. Generate audit trails via CSV reports

## Development Guidelines

### File Structure
```
files-refresher/
├── file_refresher.py      # Main application
├── config.yaml            # User configuration
├── requirements.txt       # Dependencies
├── README.md             # Basic documentation
├── PROJECT_DESIGN.md     # Detailed design doc
├── USER_GUIDE.md         # End-user guide
└── CLAUDE.md            # This file
```

### Code Style
- Clear function names that describe the action
- Comprehensive error handling with user-friendly messages
- Progress feedback for long operations
- Validation before destructive operations

### Testing Considerations
- Test with files that already have dates
- Test with mixed date formats
- Test with read-only files
- Test with very long paths
- Test with Unicode filenames

## Common Tasks

### Adding New File Extensions
Edit `config.yaml`:
```yaml
rename_extensions:
  - .newext
```

### Changing UI Colors
Modify the Rich console theme and style definitions

### Adding New Report Columns
1. Update CSV writer headers
2. Add data collection during file processing
3. Update documentation

## Edge Cases to Handle
1. Files with existing dates in different formats
2. Read-only files or directories
3. Files being used by other processes
4. Very long file paths (Windows limit)
5. Unicode/special characters in filenames
6. Network drives or cloud-synced folders

## Future Enhancement Ideas
- Undo functionality
- Scheduled runs
- Email reports
- GUI version
- Cloud storage integration