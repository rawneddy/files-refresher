# TODO - File Retention Refresher Implementation

## Overview
This document outlines the implementation plan broken into logical checkins. Each phase builds upon the previous and can be tested independently.

## Phase 1: Core Foundation ✅ COMPLETED
**Goal**: Basic script structure with file operations and configuration

### Tasks
- [x] Create `file_refresher.py` with main structure
- [x] Create `config.yaml` with default settings
- [x] Create `requirements.txt` with dependencies
- [x] Implement file scanning and metadata reading
- [x] Implement date detection patterns (YYYY.MM.DD, YYYY-MM-DD)
- [x] Implement modification date update functionality
- [x] Basic command-line argument parsing
- [x] Create sample test files for development

### Deliverables
- Working script that can scan directories and update file dates
- Configuration system in place
- Basic testing capability

### Commit Message
`feat: implement core file operations and configuration system`

---

## Phase 2: Retro UI Implementation ✅ COMPLETED
**Goal**: Apple II-style interface with Rich library

### Tasks
- [x] Implement Rich console with retro green theme
- [x] Create welcome screen with ASCII art
- [x] Implement directory selection wizard
- [x] Create configuration review screen
- [x] Implement pre-scan summary display
- [x] Add confirmation prompts
- [x] Create progress bar with file counter
- [x] Implement completion summary screen

### Deliverables
- Full retro UI experience
- User-friendly wizard flow
- Visual feedback during processing

### Commit Message
`feat: add retro Apple II-style UI with Rich library`

---

## Phase 3: File Processing & Reporting ✅ Ready after Phase 2
**Goal**: Complete file renaming logic and CSV reporting

### Tasks
- [ ] Implement intelligent file renaming with date prefix
- [ ] Handle all date format conversions
- [ ] Create CSV report generation
- [ ] Add enhanced columns (path, dates, extension, size)
- [ ] Implement error handling for locked/readonly files
- [ ] Add logging system for debugging
- [ ] Test with various file types and edge cases

### Deliverables
- Full rename functionality
- Comprehensive CSV reports
- Robust error handling

### Commit Message
`feat: implement file renaming logic and CSV reporting`

---

## Phase 4: Advanced Modes ✅ Ready after Phase 3
**Goal**: CSV input mode and dry-run capability

### Tasks
- [ ] Add mode selection (Directory vs CSV input)
- [ ] Implement CSV input file parsing and validation
- [ ] Add operation type selection (Process vs Report Only)
- [ ] Implement dry-run mode that generates report without changes
- [ ] Add CSV format validation and error messages
- [ ] Test workflow: Directory scan → Edit CSV → Process specific files

### Deliverables
- Multiple operation modes
- Dry-run capability
- CSV-based targeting

### Commit Message
`feat: add CSV input mode and dry-run functionality`

---

## Phase 5: Build & Distribution ✅ Ready after Phase 4
**Goal**: Windows executable and distribution package

### Tasks
- [ ] Create `create_icon.py` and generate icon.ico
- [ ] Create `build_windows.bat` script
- [ ] Create `file_refresher.spec` for PyInstaller
- [ ] Test executable on Windows
- [ ] Create README.md with quick start guide
- [ ] Update all documentation with final details
- [ ] Create sample directory structure for testing
- [ ] Package distribution files

### Deliverables
- Windows executable
- Complete documentation
- Ready-to-distribute package

### Commit Message
`feat: add Windows build system and distribution package`

---

## Testing Checklist
After each phase, test:
- [ ] Basic functionality works as expected
- [ ] No regression from previous phase
- [ ] Error cases handled gracefully
- [ ] Documentation matches implementation

## Notes
- Each phase should be fully functional before moving to next
- Run tests with sample files after each phase
- Update CLAUDE.md if any design decisions change
- Keep commit messages consistent with conventional commits