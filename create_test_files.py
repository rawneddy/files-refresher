#!/usr/bin/env python3
"""Create test files for development and testing"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def create_test_files():
    test_dir = Path("test_files")
    
    # Remove the entire directory if it exists, then recreate it
    if test_dir.exists():
        print(f"Removing existing '{test_dir}' directory...")
        try:
            shutil.rmtree(test_dir)
        except PermissionError as e:
            print(f"ERROR: Permission denied removing directory: {e}")
            print("Try running as administrator or check if files are in use")
            return
        except Exception as e:
            print(f"ERROR: Failed to remove directory: {e}")
            return
    
    # Create fresh directory
    print(f"Creating fresh '{test_dir}' directory...")
    test_dir.mkdir()
    
    # Generate 50 test files with variety
    test_files = [
        # Microsoft Office files (.docx) - Multiple instances
        ("Budget Report.xlsx", 90),
        ("Financial Analysis.xlsx", 120),
        ("Q1 Sales Data.xlsx", 180),
        ("Inventory Report.xlsx", 365),
        ("Employee Data.xlsx", 45),
        ("Marketing Metrics.xlsx", 200),
        
        # Excel legacy (.xls)
        ("Legacy Database.xls", 500),
        ("Old Budget.xls", 400),
        ("Archive Spreadsheet.xls", 300),
        
        # Word documents (.docx)
        ("Project Plan.docx", 365),
        ("Meeting Minutes.docx", 90),
        ("Policy Manual.docx", 250),
        ("Training Guide.docx", 150),
        ("Contract Template.docx", 75),
        
        # Word legacy (.doc)
        ("Old Contract.doc", 800),
        ("Legacy Manual.doc", 600),
        ("Archive Document.doc", 450),
        
        # PowerPoint presentations (.pptx)
        ("Presentation.pptx", 180),
        ("Sales Pitch.pptx", 120),
        ("Training Slides.pptx", 90),
        ("Company Overview.pptx", 240),
        
        # PowerPoint legacy (.ppt)
        ("Old Presentation.ppt", 700),
        ("Legacy Training.ppt", 550),
        
        # Microsoft Visio (.vsdx)
        ("Network Diagram.vsdx", 160),
        ("Process Flow.vsdx", 220),
        ("System Architecture.vsdx", 95),
        
        # Visio legacy (.vsd)
        ("Legacy Flowchart.vsd", 650),
        ("Old Network Map.vsd", 480),
        
        # Files with existing dates (dots format - no change needed)
        ("2019.06.15 Meeting Notes.docx", 45),
        ("2018.12.25 Holiday Schedule.xlsx", 100),
        ("2020.03.10 Project Specs.pptx", 85),
        ("2017.11.20 Legacy Report.doc", 300),
        
        # Files with existing dates (hyphens - need conversion to dots)
        ("2020-03-14 Budget Draft.xlsx", 60),
        ("2019-11-30 Year End Report.docx", 200),
        ("2021-01-15 Strategic Plan.pptx", 140),
        ("2018-05-22 System Design.vsdx", 280),
        
        # Files with year+month only (need day added as .01)
        ("2023.06 Budget Summary.xlsx", 120),
        ("2024.03 Marketing Plan.docx", 90),
        ("2022.11 Sales Report.pptx", 180),
        ("2023.09 Network Design.vsdx", 150),
        
        # Non-office files (shouldn't be renamed but dates updated if old)
        ("readme.txt", 400),
        ("installation_guide.txt", 120),
        ("config_backup.json", 180),
        ("data_export.csv", 90),
        ("backup_data.csv", 250),
        ("system_log.log", 340),
        ("error_report.log", 95),
        ("company_logo.png", 50),
        ("diagram.jpg", 300),
        ("screenshot.png", 45),
        
        # Recent files (shouldn't update date or rename)
        ("Recent Document.docx", 5),
        ("New Spreadsheet.xlsx", 10),
        ("Current Presentation.pptx", 15),
        ("Today Notes.txt", 2),
    ]
    
    created_count = 0
    for filename, days_old in test_files:
        file_path = test_dir / filename
        
        try:
            # Create file
            file_path.write_text(f"Test file: {filename}")
            
            # Set modification date
            old_date = datetime.now() - timedelta(days=days_old)
            timestamp = old_date.timestamp()
            os.utime(file_path, (timestamp, timestamp))
            
            print(f"Created: {filename} ({days_old} days old)")
            created_count += 1
            
        except PermissionError as e:
            print(f"ERROR: Permission denied creating '{filename}': {e}")
        except Exception as e:
            print(f"ERROR: Failed to create '{filename}': {e}")
    
    if created_count != len(test_files):
        print(f"\nWARNING: Only {created_count} of {len(test_files)} files were created successfully")
    
    print(f"\nCreated {created_count} test files in '{test_dir}' directory")
    print(f"File breakdown:")
    print(f"  - Excel files (.xlsx/.xls): {len([f for f in test_files if f[0].endswith(('.xlsx', '.xls'))])}")
    print(f"  - Word files (.docx/.doc): {len([f for f in test_files if f[0].endswith(('.docx', '.doc'))])}")
    print(f"  - PowerPoint files (.pptx/.ppt): {len([f for f in test_files if f[0].endswith(('.pptx', '.ppt'))])}")
    print(f"  - Visio files (.vsdx/.vsd): {len([f for f in test_files if f[0].endswith(('.vsdx', '.vsd'))])}")
    print(f"  - Other files: {len([f for f in test_files if not f[0].endswith(('.xlsx', '.xls', '.docx', '.doc', '.pptx', '.ppt', '.vsdx', '.vsd'))])}")
    
    # Count files by age category
    old_files = len([f for f in test_files if f[1] > 30])
    recent_files = len([f for f in test_files if f[1] <= 30])
    print(f"\nAge distribution:")
    print(f"  - Files older than 30 days: {old_files}")
    print(f"  - Recent files (≤30 days): {recent_files}")
    
    # Count files by date pattern for testing
    import re
    dots_pattern = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})\s+(.+)$')
    hyphens_pattern = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\s+(.+)$')
    year_month_pattern = re.compile(r'^(\d{4})\.(\d{2})\s+(.+)$')
    
    dots_count = len([f for f in test_files if dots_pattern.match(f[0])])
    hyphens_count = len([f for f in test_files if hyphens_pattern.match(f[0])])
    year_month_count = len([f for f in test_files if year_month_pattern.match(f[0])])
    no_date_count = len([f for f in test_files if not (dots_pattern.match(f[0]) or hyphens_pattern.match(f[0]) or year_month_pattern.match(f[0]))])
    
    print(f"\nDate pattern distribution:")
    print(f"  - YYYY.MM.DD format: {dots_count}")
    print(f"  - YYYY-MM-DD format: {hyphens_count}")
    print(f"  - YYYY.MM format: {year_month_count}")
    print(f"  - No date prefix: {no_date_count}")

if __name__ == "__main__":
    create_test_files()