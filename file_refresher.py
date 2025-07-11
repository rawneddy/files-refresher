#!/usr/bin/env python3
"""
File Retention Refresher with Retro UI
Updates file modification dates and renames files with original dates
"""

import os
import sys
import argparse
import re
import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import time
from typing import Optional, List, Dict, Tuple
from collections import defaultdict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich.box import DOUBLE, HEAVY, ASCII
from rich.theme import Theme
from rich.style import Style

# Define retro green theme
RETRO_THEME = Theme({
    "primary": "bright_green",
    "secondary": "green",
    "accent": "bright_white",
    "error": "bright_red",
    "warning": "yellow",
    "info": "cyan",
    "border": "#33FF33",
    "title": "bold bright_green",
    "prompt": "bright_green"
})

class FileRefresher:
    def __init__(self, config_path="config.yaml", interactive=True):
        self.config = self._load_config(config_path)
        self.rename_extensions = [ext.lower() for ext in self.config.get('rename_extensions', [])]
        self.days_threshold = self.config.get('days_threshold', 30)
        self.report_settings = self.config.get('report', {})
        self.processed_files = []
        self.interactive = interactive
        self.console = Console(theme=RETRO_THEME, force_terminal=True)
        self.errors = []
        self.dry_run = False
        self.setup_logging()
        
        # Date patterns
        self.date_pattern_dots = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})\s+(.+)$')
        self.date_pattern_hyphens = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\s+(.+)$')
        
    def setup_logging(self):
        """Setup logging for error tracking"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_refresher.log'),
                logging.StreamHandler() if not self.interactive else logging.NullHandler()
            ]
        )
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            if self.interactive:
                self.console.print(f"[warning]Warning: {config_path} not found. Using default settings.[/warning]")
            return self._get_default_config()
        except Exception as e:
            if self.interactive:
                self.console.print(f"[error]Error loading config: {e}. Using default settings.[/error]")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Return default configuration"""
        return {
            'rename_extensions': ['.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.vsdx', '.vsd', '.pdf'],
            'days_threshold': 30,
            'report': {
                'filename_pattern': 'file_refresh_report_{date}.csv',
                'save_in_target_directory': True
            }
        }
    
    def show_welcome_screen(self):
        """Display retro welcome screen"""
        self.console.clear()
        
        # ASCII Art Logo
        logo = """
╔═══════════════════════════════════════════════════╗
║          FILE RETENTION REFRESHER v1.0            ║
║              [ APPLE ][ STYLE ]                   ║
╚═══════════════════════════════════════════════════╝
"""
        
        self.console.print(logo, style="primary", justify="center")
        self.console.print("\n")
        self.console.print("Avoid retention constraints by refreshing file dates", style="secondary", justify="center")
        self.console.print("and preserving original dates in filenames", style="secondary", justify="center")
        self.console.print("\n")
        
        # Blinking cursor effect
        with self.console.status("[primary]Press ENTER to continue...[/primary]", spinner="dots"):
            input()
    
    def _show_step_header(self, title: str, step_info: str = "", selected_path: str = ""):
        """Show consistent header for each step"""
        # Mini logo for consistency
        self.console.print("╔═══════════════════════════════════════════════════╗", style="border")
        self.console.print("║          FILE RETENTION REFRESHER v1.0            ║", style="title")
        self.console.print("║              [ APPLE ][ STYLE ]                   ║", style="title")
        self.console.print("╚═══════════════════════════════════════════════════╝", style="border")
        
        if step_info:
            self.console.print(f"\n[info]{step_info}[/info]")
            
        if selected_path:
            # Truncate path if too long for display
            display_path = selected_path
            if len(display_path) > 45:
                display_path = "..." + display_path[-42:]
            self.console.print(f"\n[accent]📁 Target: {display_path}[/accent]")
        
        self.console.print(f"\n[primary]{title}[/primary]")
        self.console.print("─" * 50, style="border")
    
    def _open_file_browser(self, title: str, filetypes: list) -> str:
        """Open a file browser dialog"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            import sys
            import os
            
            # Suppress macOS NSWindow warnings
            if sys.platform == 'darwin':
                os.environ['TK_SILENCE_DEPRECATION'] = '1'
            
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Platform-specific window handling
            if sys.platform == 'darwin':
                root.call('wm', 'attributes', '.', '-topmost', '1')
            else:
                root.attributes('-topmost', True)
            
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title=f"Select {title}",
                filetypes=filetypes
            )
            
            root.destroy()  # Clean up
            return file_path
            
        except ImportError:
            self.console.print("\n[error]✗ File browser not available (tkinter not installed)[/error]")
            return ""
        except Exception as e:
            self.console.print(f"\n[error]✗ Error opening file browser: {e}[/error]")
            return ""
    
    def _open_directory_browser(self) -> str:
        """Open a directory browser dialog"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            import sys
            import os
            
            # Suppress macOS NSWindow warnings
            if sys.platform == 'darwin':
                os.environ['TK_SILENCE_DEPRECATION'] = '1'
            
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Platform-specific window handling
            if sys.platform == 'darwin':
                root.call('wm', 'attributes', '.', '-topmost', '1')
            else:
                root.attributes('-topmost', True)
            
            # Open directory dialog
            directory_path = filedialog.askdirectory(
                title="Select target directory"
            )
            
            root.destroy()  # Clean up
            return directory_path
            
        except ImportError:
            self.console.print("\n[error]✗ Directory browser not available (tkinter not installed)[/error]")
            return ""
        except Exception as e:
            self.console.print(f"\n[error]✗ Error opening directory browser: {e}[/error]")
            return ""
    
    def get_mode_selection(self) -> str:
        """Get user selection for operation mode"""
        self.console.clear()
        self._show_step_header("MODE SELECTION", "Step 2 of 4")
        
        self.console.print("\n[accent]Choose operation mode:[/accent]")
        self.console.print("[secondary]D[/secondary] - Directory Mode: Process all files in a directory")
        self.console.print("[secondary]C[/secondary] - CSV Input Mode: Process only files listed in CSV")
        
        while True:
            choice = Prompt.ask("\n[prompt]> SELECT MODE [D/C][/prompt]", choices=["D", "C", "d", "c"], default="D")
            return choice.upper()
    
    def get_operation_type(self, selected_path: str = "") -> str:
        """Get user selection for operation type (Directory mode only)"""
        self.console.clear()
        self._show_step_header("OPERATION TYPE", "Step 4 of 4", selected_path)
        
        self.console.print("\n[accent]Choose operation type:[/accent]")
        self.console.print("[secondary]P[/secondary] - Process Files: Make actual changes to files")
        self.console.print("[secondary]R[/secondary] - Report Only: Generate CSV report without making changes (dry run)")
        
        while True:
            choice = Prompt.ask("\n[prompt]> OPERATION TYPE [P/R][/prompt]", choices=["P", "R", "p", "r"], default="P")
            return choice.upper()
    
    def get_csv_input(self) -> str:
        """Get CSV input file path with validation"""
        self.console.clear()
        self._show_step_header("CSV INPUT SELECTION", "Step 3 of 3")
        
        self.console.print("\n[accent]Select your CSV file:[/accent]")
        self.console.print("[secondary]• Type the full path to your CSV file[/secondary]")
        self.console.print("[secondary]• Drag and drop your CSV file into this terminal[/secondary]")
        self.console.print("[secondary]• Type 'browse' to open a file browser[/secondary]")
        self.console.print("[secondary]• Press Enter after pasting/dropping the path[/secondary]")
        
        while True:
            csv_path = Prompt.ask("\n[prompt]> CSV INPUT FILE (drag & drop, type path, or 'browse')[/prompt]")
            
            # Check if user wants to browse
            if csv_path.lower().strip() == 'browse':
                csv_path = self._open_file_browser("CSV files", [("CSV files", "*.csv"), ("All files", "*.*")])
                if not csv_path:  # User cancelled
                    continue
            
            # Handle drag-and-drop path formatting
            # Remove line breaks, surrounding quotes, and handle escaped characters
            original_path = csv_path
            csv_path = csv_path.replace('\n', '').replace('\r', '')  # Remove line breaks
            csv_path = csv_path.strip().strip('"').strip("'")  # Remove quotes
            csv_path = csv_path.replace('\\ ', ' ')  # Handle escaped spaces (macOS/Linux)
            csv_path = csv_path.replace('\\~', '~')  # Handle escaped tildes
            
            # Debug output when path looks like it was drag-and-dropped
            if original_path != csv_path and len(original_path) > 50:
                self.console.print(f"\n[info]📋 Processed drag-and-drop path[/info]")
            
            path = Path(csv_path).expanduser().resolve()
            
            if not path.exists():
                self.console.print(f"\n[error]✗ File not found: {csv_path}[/error]")
                continue
            
            if not path.is_file():
                self.console.print(f"\n[error]✗ Not a file: {csv_path}[/error]")
                continue
            
            if path.suffix.lower() != '.csv':
                self.console.print(f"\n[error]✗ Not a CSV file: {csv_path}[/error]")
                continue
            
            # Validate CSV format
            try:
                if self.validate_csv_format(path):
                    self.console.print(f"\n[info]✓ CSV file validated: {path}[/info]")
                    return str(path)
                else:
                    self.console.print(f"\n[error]✗ Invalid CSV format[/error]")
            except Exception as e:
                self.console.print(f"\n[error]✗ Error reading CSV: {e}[/error]")
    
    def validate_csv_format(self, csv_path: Path) -> bool:
        """Validate CSV file has required columns"""
        required_columns = {'new_path', 'original_modified', 'new_modified', 'extension', 'size_bytes'}
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                columns = set(reader.fieldnames or [])
                
                if not required_columns.issubset(columns):
                    missing = required_columns - columns
                    self.console.print(f"\n[error]Missing required columns: {', '.join(missing)}[/error]")
                    return False
                
                # Check if file has data
                row_count = sum(1 for _ in reader)
                if row_count == 0:
                    self.console.print("\n[warning]CSV file is empty[/warning]")
                    return False
                
                self.console.print(f"\n[info]CSV contains {row_count} files[/info]")
                return True
                
        except Exception as e:
            self.console.print(f"\n[error]Error validating CSV: {e}[/error]")
            return False
    
    def get_directory_input(self) -> str:
        """Get directory path from user with validation"""
        self.console.clear()
        self._show_step_header("DIRECTORY SELECTION", "Step 3 of 4")
        
        self.console.print("\n[accent]Select target directory:[/accent]")
        self.console.print("[secondary]• Type the full path to your directory[/secondary]")
        self.console.print("[secondary]• Drag and drop a folder into this terminal[/secondary]")
        self.console.print("[secondary]• Type 'browse' to open a folder browser[/secondary]")
        self.console.print(f"[secondary]• Press Enter for current directory: {os.getcwd()}[/secondary]")
        
        while True:
            directory = Prompt.ask(
                "\n[prompt]> SELECT DIRECTORY (drag & drop, type path, or 'browse')[/prompt]",
                default=os.getcwd()
            )
            
            # Check if user wants to browse
            if directory.lower().strip() == 'browse':
                directory = self._open_directory_browser()
                if not directory:  # User cancelled
                    continue
            
            # Handle drag-and-drop path formatting
            # Remove line breaks, surrounding quotes, and handle escaped characters
            original_directory = directory
            directory = directory.replace('\n', '').replace('\r', '')  # Remove line breaks
            directory = directory.strip().strip('"').strip("'")  # Remove quotes
            directory = directory.replace('\\ ', ' ')  # Handle escaped spaces (macOS/Linux)
            directory = directory.replace('\\~', '~')  # Handle escaped tildes
            
            # Debug output when path looks like it was drag-and-dropped
            if original_directory != directory and len(original_directory) > 50:
                self.console.print(f"\n[info]📋 Processed drag-and-drop path[/info]")
            
            path = Path(directory).expanduser().resolve()
            
            if path.exists() and path.is_dir():
                self.console.print(f"\n[info]✓ Directory confirmed: {path}[/info]")
                return str(path)
            else:
                self.console.print(f"\n[error]✗ Invalid directory: {directory}[/error]")
                self.console.print("[warning]Please enter a valid directory path[/warning]")
    
    def show_config_review(self):
        """Display configuration review screen"""
        self.console.clear()
        self._show_step_header("CONFIGURATION REVIEW", "Step 1 of 4")
        
        self.console.print("\n[accent]Review default settings before proceeding:[/accent]")
        
        # Create extensions table
        self.console.print("\n[primary]RENAME SETTINGS[/primary]")
        self.console.print("[secondary]Files will be renamed with original date prefix (YYYY.MM.DD format)[/secondary]")
        
        table = Table(
            box=ASCII,
            style="primary",
            border_style="border",
            show_header=True
        )
        
        table.add_column("Extension", style="accent")
        table.add_column("File Type", style="secondary")
        
        # Extension descriptions
        ext_descriptions = {
            '.docx': 'Word Documents',
            '.doc': 'Legacy Word',
            '.xlsx': 'Excel Spreadsheets',
            '.xls': 'Legacy Excel',
            '.pptx': 'PowerPoint Presentations',
            '.ppt': 'Legacy PowerPoint',
            '.vsdx': 'Visio Diagrams',
            '.vsd': 'Legacy Visio',
            '.pdf': 'PDF Documents'
        }
        
        for ext in self.rename_extensions:
            desc = ext_descriptions.get(ext, 'Custom File Type')
            table.add_row(f"✓ {ext}", desc)
        
        self.console.print("\n")
        self.console.print(table)
        
        self.console.print(f"\n[primary]MODIFICATION DATE UPDATE:[/primary]")
        self.console.print(f"├─ ALL files older than [accent]{self.days_threshold} days[/accent]")
        self.console.print(f"└─ Will be updated to: [accent]{datetime.now().strftime('%Y.%m.%d')}[/accent]")
        
        self.console.print("\n[info][ To modify these settings, edit config.yaml ][/info]")
        
        if not Confirm.ask("\n[prompt]CONTINUE WITH THESE SETTINGS?[/prompt]", default=True):
            self.console.print("\n[warning]Operation cancelled by user[/warning]")
            sys.exit(0)
    
    def scan_directory(self, directory_path, recursive=True):
        """Scan directory and return list of files with metadata"""
        files = []
        path = Path(directory_path)
        
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        # Show scanning progress
        with self.console.status("[primary]SCANNING DIRECTORY...[/primary]", spinner="dots"):
            # Use glob pattern for recursive or non-recursive search
            pattern = "**/*" if recursive else "*"
            
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    # Skip all CSV files (report files, sample files, etc.)
                    if file_path.suffix.lower() == '.csv':
                        continue
                    
                    try:
                        stat = file_path.stat()
                        files.append({
                            'path': file_path,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'extension': file_path.suffix.lower()
                        })
                    except Exception as e:
                        self.console.print(f"[error]Error reading file {file_path}: {e}[/error]")
        
        return files
    
    def show_pre_scan_summary(self, files: List[Dict], selected_path: str = "") -> bool:
        """Display pre-scan summary and get confirmation"""
        self.console.clear()
        self._show_step_header("FILE SCAN RESULTS", "Review before processing", selected_path)
        # Categorize files
        stats = defaultdict(int)
        already_dated_dots = 0
        already_dated_hyphens = 0
        will_rename = 0
        will_update_date = 0
        
        for file_info in files:
            filename = file_info['path'].name
            ext = file_info['extension']
            
            # Count by extension
            stats[ext] += 1
            
            # Check date patterns
            if self.date_pattern_dots.match(filename):
                already_dated_dots += 1
            elif self.date_pattern_hyphens.match(filename):
                already_dated_hyphens += 1
                if ext in self.rename_extensions:
                    will_rename += 1
            elif ext in self.rename_extensions:
                will_rename += 1
            
            # Check if needs date update
            if self.needs_date_update(file_info):
                will_update_date += 1
        
        # Display summary table
        self.console.print("\n[primary]FILE TYPE SUMMARY:[/primary]")
        
        table = Table(box=ASCII, style="primary", border_style="border")
        table.add_column("File Type", style="accent")
        table.add_column("Count", justify="right", style="secondary")
        
        # Add common file types
        common_exts = ['.docx', '.xlsx', '.pptx', '.pdf', '.doc', '.xls', '.ppt']
        for ext in common_exts:
            if stats[ext] > 0:
                table.add_row(f"{ext.upper()[1:]} Files ({ext})", str(stats[ext]))
        
        # Add other extensions
        for ext, count in sorted(stats.items()):
            if ext not in common_exts and count > 0:
                table.add_row(f"Other ({ext})", str(count))
        
        self.console.print(table)
        
        # Summary statistics
        self.console.print("\n[primary]PROCESSING SUMMARY:[/primary]")
        self.console.print(f"├─ Files already dated (YYYY.MM.DD): [accent]{already_dated_dots}[/accent]")
        self.console.print(f"├─ Files already dated (YYYY-MM-DD): [accent]{already_dated_hyphens}[/accent]")
        self.console.print(f"├─ Files to rename: [accent]{will_rename}[/accent]")
        self.console.print(f"├─ Dates to update: [accent]{will_update_date}[/accent]")
        self.console.print(f"└─ TOTAL FILES: [accent]{len(files)}[/accent]")
        
        return Confirm.ask("\n[prompt]PROCEED WITH FILE PROCESSING?[/prompt]", default=True)
    
    def needs_date_update(self, file_info):
        """Check if file modification date needs updating"""
        age_threshold = datetime.now() - timedelta(days=self.days_threshold)
        return file_info['modified'] < age_threshold
    
    def needs_rename(self, file_info):
        """Check if file needs to be renamed with date prefix"""
        # Check if extension is in rename list
        if file_info['extension'] not in self.rename_extensions:
            return False, None
        
        filename = file_info['path'].name
        
        # Check if already has YYYY.MM.DD format
        if self.date_pattern_dots.match(filename):
            return False, 'already_has_dots'
        
        # Check if has YYYY-MM-DD format (needs conversion)
        if self.date_pattern_hyphens.match(filename):
            return True, 'convert_hyphens'
        
        # No date prefix, needs to be added
        return True, 'add_date'
    
    def get_new_filename(self, file_info, rename_reason):
        """Generate new filename based on rename reason"""
        filename = file_info['path'].name
        
        if rename_reason == 'convert_hyphens':
            # Convert YYYY-MM-DD to YYYY.MM.DD
            match = self.date_pattern_hyphens.match(filename)
            if match:
                year, month, day, rest = match.groups()
                return f"{year}.{month}.{day} {rest}"
        
        elif rename_reason == 'add_date':
            # Add date prefix from original modification date
            date_str = file_info['modified'].strftime('%Y.%m.%d')
            return f"{date_str} {filename}"
        
        return filename
    
    def update_file_modified_date(self, file_path, new_date=None):
        """Update file modification date with enhanced error handling"""
        if new_date is None:
            new_date = datetime.now()
        
        # Convert to timestamp
        timestamp = new_date.timestamp()
        
        try:
            # Check if file is read-only and temporarily change permissions
            original_mode = None
            if not os.access(file_path, os.W_OK):
                try:
                    original_mode = file_path.stat().st_mode
                    file_path.chmod(original_mode | 0o200)  # Add write permission
                except Exception as perm_error:
                    error_msg = f"Cannot modify read-only file {file_path}: {perm_error}"
                    self.errors.append(error_msg)
                    logging.warning(error_msg)
                    if self.interactive:
                        self.console.print(f"[warning]Skipping read-only file: {file_path.name}[/warning]")
                    return False
            
            # Update both access and modification times
            os.utime(file_path, (timestamp, timestamp))
            
            # Restore original permissions if we changed them
            if original_mode is not None:
                try:
                    file_path.chmod(original_mode)
                except Exception:
                    pass  # Don't fail if we can't restore permissions
            
            return True
            
        except PermissionError as e:
            error_msg = f"Permission denied updating {file_path}: {e}"
            self.errors.append(error_msg)
            logging.error(error_msg)
            if self.interactive:
                self.console.print(f"[error]Permission denied: {file_path.name}[/error]")
            return False
        except Exception as e:
            error_msg = f"Error updating date for {file_path}: {e}"
            self.errors.append(error_msg)
            logging.error(error_msg)
            if self.interactive:
                self.console.print(f"[error]Error updating {file_path.name}: {e}[/error]")
            return False
    
    def rename_file(self, file_path, new_name):
        """Rename file to new name with enhanced error handling"""
        try:
            new_path = file_path.parent / new_name
            
            # Check if target already exists
            if new_path.exists():
                # Special case: if source and target are the same, file is already correctly named
                if file_path.name == new_name:
                    logging.info(f"File already correctly named: {file_path.name}")
                    if self.interactive:
                        self.console.print(f"[info]Already correctly named: {file_path.name}[/info]")
                    return str(new_path)
                else:
                    error_msg = f"Target file already exists: {new_path}"
                    self.errors.append(error_msg)
                    logging.warning(error_msg)
                    if self.interactive:
                        self.console.print(f"[warning]Target exists, skipping: {new_name}[/warning]")
                    return None
            
            # Check if filename is too long for filesystem
            if len(new_name) > 255:  # Most filesystems limit to 255 chars
                error_msg = f"Filename too long: {new_name[:50]}..."
                self.errors.append(error_msg)
                logging.warning(error_msg)
                if self.interactive:
                    self.console.print(f"[warning]Filename too long, skipping: {file_path.name}[/warning]")
                return None
            
            # Perform the rename
            file_path.rename(new_path)
            logging.info(f"Renamed: {file_path.name} -> {new_name}")
            return new_path
            
        except PermissionError as e:
            error_msg = f"Permission denied renaming {file_path}: {e}"
            self.errors.append(error_msg)
            logging.error(error_msg)
            if self.interactive:
                self.console.print(f"[error]Permission denied renaming: {file_path.name}[/error]")
            return None
        except OSError as e:
            error_msg = f"OS error renaming {file_path}: {e}"
            self.errors.append(error_msg)
            logging.error(error_msg)
            if self.interactive:
                self.console.print(f"[error]OS error renaming: {file_path.name}[/error]")
            return None
        except Exception as e:
            error_msg = f"Unexpected error renaming {file_path}: {e}"
            self.errors.append(error_msg)
            logging.error(error_msg)
            if self.interactive:
                self.console.print(f"[error]Error renaming {file_path.name}: {e}[/error]")
            return None
    
    def process_file(self, file_info):
        """Process a single file with dry-run support"""
        result = {
            'original_path': file_info['path'].resolve(),
            'new_path': file_info['path'].resolve(),
            'original_modified': file_info['modified'],
            'new_modified': file_info['modified'],
            'extension': file_info['extension'].replace('.', ''),
            'size_bytes': file_info['size'],
            'renamed': False,
            'date_updated': False
        }
        
        # Check if needs renaming
        needs_rename, rename_reason = self.needs_rename(file_info)
        
        if needs_rename:
            new_filename = self.get_new_filename(file_info, rename_reason)
            
            if self.dry_run:
                # Simulate renaming for dry run
                result['new_path'] = (file_info['path'].parent / new_filename).resolve()
                result['renamed'] = True
                logging.info(f"DRY RUN - Would rename: {file_info['path'].name} -> {new_filename}")
            else:
                # Actually rename the file
                new_path = self.rename_file(file_info['path'], new_filename)
                if new_path:
                    result['new_path'] = Path(new_path).resolve()
                    result['renamed'] = True
                    file_info['path'] = Path(new_path).resolve()  # Update for date modification
        
        # Check if needs date update
        if self.needs_date_update(file_info):
            if self.dry_run:
                # Simulate date update for dry run
                result['new_modified'] = datetime.now()
                result['date_updated'] = True
                logging.info(f"DRY RUN - Would update date: {result['new_path']}")
            else:
                # Actually update the date
                if self.update_file_modified_date(result['new_path']):
                    result['new_modified'] = datetime.now()
                    result['date_updated'] = True
        
        return result
    
    def generate_csv_report(self, results, directory_path):
        """Generate comprehensive CSV report"""
        # Generate report filename with version counter
        date_str = datetime.now().strftime('%Y.%m.%d')
        filename_pattern = self.report_settings.get('filename_pattern', 'file_refresh_report_{date}.csv')
        base_filename = filename_pattern.format(date=date_str)
        
        # Determine report location
        if self.report_settings.get('save_in_target_directory', True):
            report_dir = Path(directory_path)
        else:
            report_dir = Path('.')
        
        # Find available filename with version counter
        base_name = Path(base_filename).stem  # filename without extension
        extension = Path(base_filename).suffix  # .csv
        
        counter = 0
        report_path = report_dir / base_filename
        
        # If file exists, add two-digit counter after date
        while report_path.exists():
            counter += 1
            # Insert counter after date: file_refresh_report_2025.07.11.01.csv
            date_part = f"{date_str}.{counter:02d}"
            versioned_filename = filename_pattern.format(date=date_part)
            report_path = report_dir / versioned_filename
        
        try:
            with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'new_path',
                    'original_modified', 
                    'new_modified',
                    'extension',
                    'size_bytes'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    # Format dates for CSV
                    original_modified = result['original_modified'].strftime('%Y-%m-%d %H:%M:%S')
                    new_modified = result['new_modified'].strftime('%Y-%m-%d %H:%M:%S')
                    
                    writer.writerow({
                        'new_path': str(result['new_path']),
                        'original_modified': original_modified,
                        'new_modified': new_modified,
                        'extension': result['extension'],
                        'size_bytes': result['size_bytes']
                    })
            
            logging.info(f"CSV report generated: {report_path}")
            return report_path
            
        except Exception as e:
            error_msg = f"Error generating CSV report: {e}"
            self.errors.append(error_msg)
            logging.error(error_msg)
            if self.interactive:
                self.console.print(f"[error]Error generating report: {e}[/error]")
            return None
    
    def process_directory_with_progress(self, directory_path):
        """Process all files in directory with progress display"""
        self.console.print(f"\n[primary]SCANNING DIRECTORY...[/primary]")
        files = self.scan_directory(directory_path)
        
        if not self.show_pre_scan_summary(files, directory_path):
            self.console.print("\n[warning]Operation cancelled by user[/warning]")
            return []
        
        self.console.print("\n[primary]PROCESSING FILES...[/primary]\n")
        
        results = []
        
        # Create progress bar
        with Progress(
            SpinnerColumn(style="primary"),
            TextColumn("[primary]{task.description}[/primary]"),
            BarColumn(complete_style="primary", finished_style="secondary"),
            TextColumn("[accent]{task.percentage:>3.0f}%[/accent]"),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Processing", total=len(files))
            
            for i, file_info in enumerate(files):
                # Update progress description
                progress.update(
                    task, 
                    description=f"[{i+1}/{len(files)}] {file_info['path'].name[:50]}...",
                    advance=1
                )
                
                result = self.process_file(file_info)
                results.append(result)
        
        return results
    
    def load_csv_file_list(self, csv_path: str) -> List[Dict]:
        """Load file list from CSV input"""
        files = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    file_path = Path(row['new_path'])
                    
                    # Check if file exists
                    if not file_path.exists():
                        error_msg = f"File not found in CSV: {file_path}"
                        self.errors.append(error_msg)
                        logging.warning(error_msg)
                        continue
                    
                    # Parse dates
                    try:
                        original_modified = datetime.strptime(row['original_modified'], '%Y-%m-%d %H:%M:%S')
                        new_modified = datetime.strptime(row['new_modified'], '%Y-%m-%d %H:%M:%S')
                    except ValueError as e:
                        error_msg = f"Invalid date format in CSV for {file_path}: {e}"
                        self.errors.append(error_msg)
                        logging.error(error_msg)
                        continue
                    
                    files.append({
                        'path': file_path,
                        'size': int(row['size_bytes']),
                        'modified': original_modified,
                        'extension': f".{row['extension']}" if not row['extension'].startswith('.') else row['extension'],
                        'csv_original_modified': original_modified,
                        'csv_new_modified': new_modified
                    })
                    
            logging.info(f"Loaded {len(files)} files from CSV: {csv_path}")
            return files
            
        except Exception as e:
            error_msg = f"Error loading CSV file {csv_path}: {e}"
            self.errors.append(error_msg)
            logging.error(error_msg)
            if self.interactive:
                self.console.print(f"[error]{error_msg}[/error]")
            return []
    
    def process_csv_files_with_progress(self, csv_path: str):
        """Process files from CSV input with progress display"""
        self.console.print(f"\n[primary]LOADING CSV FILE...[/primary]")
        files = self.load_csv_file_list(csv_path)
        
        if not files:
            self.console.print("\n[error]No valid files found in CSV[/error]")
            return []
        
        # Show summary
        self.console.print(f"\n[primary]CSV INPUT SUMMARY:[/primary]")
        self.console.print(f"└─ Files to process: [accent]{len(files)}[/accent]")
        
        if not Confirm.ask("\n[prompt]PROCEED WITH CSV FILE PROCESSING?[/prompt]", default=True):
            self.console.print("\n[warning]Operation cancelled by user[/warning]")
            return []
        
        self.console.print("\n[primary]PROCESSING FILES...[/primary]\n")
        
        results = []
        
        # Create progress bar
        with Progress(
            SpinnerColumn(style="primary"),
            TextColumn("[primary]{task.description}[/primary]"),
            BarColumn(complete_style="primary", finished_style="secondary"),
            TextColumn("[accent]{task.percentage:>3.0f}%[/accent]"),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Processing", total=len(files))
            
            for i, file_info in enumerate(files):
                # Update progress description
                progress.update(
                    task, 
                    description=f"[{i+1}/{len(files)}] {file_info['path'].name[:50]}...",
                    advance=1
                )
                
                result = self.process_file(file_info)
                results.append(result)
        
        return results
    
    def show_completion_summary(self, results, selected_path: str = ""):
        """Display completion summary"""
        self.console.clear()
        self._show_step_header("PROCESSING COMPLETE", "Operation finished", selected_path)
        renamed_count = sum(1 for r in results if r['renamed'])
        updated_count = sum(1 for r in results if r['date_updated'])
        
        summary_table = Table(box=None, show_header=False, style="secondary")
        summary_table.add_column("Label", style="accent")
        summary_table.add_column("Value", justify="right", style="primary")
        
        summary_table.add_row("Files Processed:", str(len(results)))
        summary_table.add_row("Files Renamed:", str(renamed_count))
        summary_table.add_row("Dates Updated:", str(updated_count))
        
        self.console.print("\n", summary_table)
        
        if renamed_count > 0 or updated_count > 0:
            self.console.print("\n[info]✓ All operations completed successfully![/info]")
        else:
            self.console.print("\n[warning]No files required processing[/warning]")
        
        # Show errors if any
        if self.errors:
            # Categorize warnings vs actual errors
            target_exists_warnings = sum(1 for error in self.errors if "Target file already exists" in error)
            other_errors = len(self.errors) - target_exists_warnings
            
            if target_exists_warnings > 0:
                self.console.print(f"\n[info]ℹ {target_exists_warnings} files were skipped (already properly named)[/info]")
                if other_errors > 0:
                    self.console.print(f"[warning]⚠ {other_errors} other warnings occurred (see file_refresher.log)[/warning]")
            else:
                self.console.print(f"\n[warning]⚠ {len(self.errors)} warnings occurred (see file_refresher.log)[/warning]")
            
            if target_exists_warnings > 0:
                self.console.print("\n[secondary]💡 Tip: Using an older CSV file may reference already-renamed files.[/secondary]")
                self.console.print("[secondary]   Use a recent CSV report for best results.[/secondary]")
    
    def show_report_location(self, report_path):
        """Display report generation confirmation"""
        if report_path:
            self.console.print(f"\n[info]📄 CSV Report saved: {report_path}[/info]")
        else:
            self.console.print("\n[error]❌ Failed to generate CSV report[/error]")

def main():
    parser = argparse.ArgumentParser(
        description="File Retention Refresher - Update file dates and rename with original dates"
    )
    parser.add_argument(
        'directory',
        nargs='?',
        help='Directory to process (interactive mode if not provided)'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--no-ui',
        action='store_true',
        help='Run without interactive UI'
    )
    parser.add_argument(
        '--csv-input',
        help='Process files from CSV input file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making them (report only)'
    )
    
    args = parser.parse_args()
    
    # Initialize refresher
    interactive = not args.no_ui and not args.directory
    refresher = FileRefresher(args.config, interactive=interactive)
    
    try:
        if interactive:
            # Interactive mode with retro UI
            refresher.show_welcome_screen()
            
            # Show configuration review first
            refresher.show_config_review()
            
            # Get mode selection
            mode = refresher.get_mode_selection()
            
            if mode == "D":
                # Directory Mode
                directory = refresher.get_directory_input()
                operation_type = refresher.get_operation_type(directory)
                
                # Set dry run mode
                refresher.dry_run = (operation_type == "R")
                
                results = refresher.process_directory_with_progress(directory)
                
                # Generate CSV report
                report_path = refresher.generate_csv_report(results, directory)
                
                # Show completion summary with dry run indication
                if refresher.dry_run:
                    refresher.console.print("\n[info]🔍 DRY RUN MODE - No files were actually modified[/info]")
                refresher.show_completion_summary(results, directory)
                refresher.show_report_location(report_path)
                
            else:
                # CSV Input Mode
                csv_path = refresher.get_csv_input()
                results = refresher.process_csv_files_with_progress(csv_path)
                
                # Generate CSV report in same directory as input CSV
                csv_dir = str(Path(csv_path).parent)
                report_path = refresher.generate_csv_report(results, csv_dir)
                
                # Show completion summary
                refresher.show_completion_summary(results, csv_path)
                refresher.show_report_location(report_path)
        else:
            # Command line mode (backward compatibility)
            refresher.interactive = False
            refresher.dry_run = args.dry_run
            
            if args.csv_input:
                # CSV Input Mode
                if not Path(args.csv_input).exists():
                    print(f"Error: CSV file not found: {args.csv_input}")
                    sys.exit(1)
                
                # Load and process files from CSV
                files = refresher.load_csv_file_list(args.csv_input)
                results = []
                for file_info in files:
                    result = refresher.process_file(file_info)
                    results.append(result)
                
                # Generate CSV report in same directory as input
                csv_dir = str(Path(args.csv_input).parent)
                report_path = refresher.generate_csv_report(results, csv_dir)
                
            else:
                # Directory Mode
                directory = args.directory or '.'
                files = refresher.scan_directory(directory)
                results = []
                for file_info in files:
                    result = refresher.process_file(file_info)
                    results.append(result)
                
                # Generate CSV report
                report_path = refresher.generate_csv_report(results, directory)
            
            # Summary
            renamed_count = sum(1 for r in results if r['renamed'])
            updated_count = sum(1 for r in results if r['date_updated'])
            
            if refresher.dry_run:
                print("\n🔍 DRY RUN MODE - No files were actually modified")
            
            print(f"\nSummary:")
            print(f"Files processed: {len(results)}")
            print(f"Files renamed: {renamed_count}")
            print(f"Dates updated: {updated_count}")
            
            if report_path:
                print(f"CSV Report saved: {report_path}")
            
            if refresher.errors:
                print(f"Errors occurred: {len(refresher.errors)} (see file_refresher.log)")
        
    except KeyboardInterrupt:
        if interactive:
            refresher.console.print("\n\n[warning]Operation cancelled by user[/warning]")
        else:
            print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        if interactive:
            refresher.console.print(f"\n[error]Error: {e}[/error]")
        else:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()