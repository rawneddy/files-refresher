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
            'rename_extensions': ['.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.pdf'],
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
    
    def get_directory_input(self) -> str:
        """Get directory path from user with validation"""
        self.console.print("\n[primary]DIRECTORY SELECTION[/primary]")
        self.console.print("─" * 50, style="border")
        
        while True:
            directory = Prompt.ask(
                "\n[prompt]> SELECT DIRECTORY[/prompt]",
                default=os.getcwd()
            )
            
            path = Path(directory).expanduser().resolve()
            
            if path.exists() and path.is_dir():
                self.console.print(f"\n[info]✓ Directory confirmed: {path}[/info]")
                return str(path)
            else:
                self.console.print(f"\n[error]✗ Invalid directory: {directory}[/error]")
                self.console.print("[warning]Please enter a valid directory path[/warning]")
    
    def show_config_review(self):
        """Display configuration review screen"""
        self.console.print("\n[primary]CONFIGURATION REVIEW:[/primary]")
        self.console.print("─" * 50, style="border")
        
        # Create extensions table
        table = Table(
            title="RENAME SETTINGS",
            box=ASCII,
            style="primary",
            title_style="title",
            border_style="border"
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
    
    def show_pre_scan_summary(self, files: List[Dict]) -> bool:
        """Display pre-scan summary and get confirmation"""
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
        """Process a single file"""
        result = {
            'original_path': file_info['path'],
            'new_path': file_info['path'],
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
            new_path = self.rename_file(file_info['path'], new_filename)
            if new_path:
                result['new_path'] = new_path
                result['renamed'] = True
                file_info['path'] = new_path  # Update for date modification
        
        # Check if needs date update
        if self.needs_date_update(file_info):
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
        
        if not self.show_pre_scan_summary(files):
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
    
    def show_completion_summary(self, results):
        """Display completion summary"""
        renamed_count = sum(1 for r in results if r['renamed'])
        updated_count = sum(1 for r in results if r['date_updated'])
        
        self.console.print("\n[primary]╔═══════════════════════════════════════╗[/primary]")
        self.console.print("[primary]║        PROCESSING COMPLETE!           ║[/primary]")
        self.console.print("[primary]╚═══════════════════════════════════════╝[/primary]")
        
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
            self.console.print(f"\n[warning]⚠ {len(self.errors)} errors occurred (see file_refresher.log)[/warning]")
    
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
    
    args = parser.parse_args()
    
    # Initialize refresher
    interactive = not args.no_ui and not args.directory
    refresher = FileRefresher(args.config, interactive=interactive)
    
    try:
        if interactive:
            # Interactive mode with retro UI
            refresher.show_welcome_screen()
            directory = refresher.get_directory_input()
            refresher.show_config_review()
            results = refresher.process_directory_with_progress(directory)
            
            # Generate CSV report
            report_path = refresher.generate_csv_report(results, directory)
            
            # Show completion summary
            refresher.show_completion_summary(results)
            refresher.show_report_location(report_path)
        else:
            # Command line mode (backward compatibility)
            directory = args.directory or '.'
            # Use simplified processing for command line mode
            refresher.interactive = False
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