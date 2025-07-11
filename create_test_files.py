#!/usr/bin/env python3
"""Create test files for development and testing"""

import os
from datetime import datetime, timedelta
from pathlib import Path

def create_test_files():
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Test files with different scenarios
    test_files = [
        # Files needing date prefix
        ("Budget Report.xlsx", 90),  # 90 days old
        ("Project Plan.docx", 365),   # 1 year old
        ("Presentation.pptx", 180),   # 6 months old
        ("Manual.pdf", 500),          # Very old
        
        # Files with existing dates (dots)
        ("2019.06.15 Meeting Notes.docx", 45),
        ("2018.12.25 Holiday Schedule.xlsx", 100),
        
        # Files with existing dates (hyphens - need conversion)
        ("2020-03-14 Budget Draft.xlsx", 60),
        ("2019-11-30 Year End Report.pdf", 200),
        
        # Non-office files (shouldn't be renamed)
        ("readme.txt", 400),
        ("data.csv", 90),
        ("image.png", 50),
        
        # Recent files (shouldn't update date)
        ("Recent Document.docx", 5),
        ("New Spreadsheet.xlsx", 10),
    ]
    
    for filename, days_old in test_files:
        file_path = test_dir / filename
        
        # Create file
        file_path.write_text(f"Test file: {filename}")
        
        # Set modification date
        old_date = datetime.now() - timedelta(days=days_old)
        timestamp = old_date.timestamp()
        os.utime(file_path, (timestamp, timestamp))
        
        print(f"Created: {filename} ({days_old} days old)")
    
    print(f"\nTest files created in '{test_dir}' directory")

if __name__ == "__main__":
    create_test_files()