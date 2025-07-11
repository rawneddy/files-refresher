#!/usr/bin/env python3
"""
File Retention Refresher with Retro UI
Updates file modification dates and renames files with original dates
"""

import os
import sys
import argparse
import re
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
        
        # Date patterns
        self.date_pattern_dots = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})\s+(.+)$')
        self.date_pattern_hyphens = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\s+(.+)$')
        
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
        """Update file modification date"""
        if new_date is None:
            new_date = datetime.now()
        
        # Convert to timestamp
        timestamp = new_date.timestamp()
        
        try:
            # Update both access and modification times
            os.utime(file_path, (timestamp, timestamp))
            return True
        except Exception as e:
            if self.interactive:
                self.console.print(f"[error]Error updating date for {file_path}: {e}[/error]")
            return False
    
    def rename_file(self, file_path, new_name):
        """Rename file to new name"""
        try:
            new_path = file_path.parent / new_name
            file_path.rename(new_path)
            return new_path
        except Exception as e:
            if self.interactive:
                self.console.print(f"[error]Error renaming {file_path}: {e}[/error]")
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
            refresher.show_completion_summary(results)
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
            
            # Summary
            renamed_count = sum(1 for r in results if r['renamed'])
            updated_count = sum(1 for r in results if r['date_updated'])
            
            print(f"\nSummary:")
            print(f"Files processed: {len(results)}")
            print(f"Files renamed: {renamed_count}")
            print(f"Dates updated: {updated_count}")
        
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