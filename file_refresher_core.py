#!/usr/bin/env python3
"""
File Retention Refresher
Updates file modification dates and renames files with original dates
"""

import os
import sys
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
import yaml

class FileRefresher:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.rename_extensions = [ext.lower() for ext in self.config.get('rename_extensions', [])]
        self.days_threshold = self.config.get('days_threshold', 30)
        self.report_settings = self.config.get('report', {})
        self.processed_files = []
        
        # Date patterns
        self.date_pattern_dots = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})\s+(.+)$')
        self.date_pattern_hyphens = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\s+(.+)$')
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: {config_path} not found. Using default settings.")
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}. Using default settings.")
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
    
    def scan_directory(self, directory_path, recursive=True):
        """Scan directory and return list of files with metadata"""
        files = []
        path = Path(directory_path)
        
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
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
                    print(f"Error reading file {file_path}: {e}")
                    
        return files
    
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
            print(f"Error updating date for {file_path}: {e}")
            return False
    
    def rename_file(self, file_path, new_name):
        """Rename file to new name"""
        try:
            new_path = file_path.parent / new_name
            file_path.rename(new_path)
            return new_path
        except Exception as e:
            print(f"Error renaming {file_path}: {e}")
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
    
    def process_directory(self, directory_path):
        """Process all files in directory"""
        print(f"Scanning directory: {directory_path}")
        files = self.scan_directory(directory_path)
        print(f"Found {len(files)} files")
        
        results = []
        for i, file_info in enumerate(files):
            print(f"Processing {i+1}/{len(files)}: {file_info['path'].name}")
            result = self.process_file(file_info)
            results.append(result)
        
        return results

def main():
    parser = argparse.ArgumentParser(
        description="File Retention Refresher - Update file dates and rename with original dates"
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to process (default: current directory)'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making them'
    )
    
    args = parser.parse_args()
    
    # Initialize refresher
    refresher = FileRefresher(args.config)
    
    try:
        # Process directory
        results = refresher.process_directory(args.directory)
        
        # Summary
        renamed_count = sum(1 for r in results if r['renamed'])
        updated_count = sum(1 for r in results if r['date_updated'])
        
        print(f"\nSummary:")
        print(f"Files processed: {len(results)}")
        print(f"Files renamed: {renamed_count}")
        print(f"Dates updated: {updated_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()