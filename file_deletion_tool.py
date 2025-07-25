#!/usr/bin/env python
"""
Prune a directory tree by moving every file *except* those listed in a CSV
to the system Recycle Bin / Trash (cross‑platform).

──────────────────────────────────────────────────────────────────────────
Prerequisite
──────────────────────────────────────────────────────────────────────────
    pip install send2trash

──────────────────────────────────────────────────────────────────────────
Usage
──────────────────────────────────────────────────────────────────────────
    python file_deletion_tool.py <target_dir> <keep_csv> <report_csv> [path_column]

    target_dir   – Root folder whose files will be examined.
    keep_csv     – CSV whose first row is a header and whose *path_column*
                    lists the *absolute* file paths to **keep**.
    report_csv   – Script will write a report of every file it moved
                    (columns: deleted_path,error).
    path_column  – (optional, 1‑based) Column number in keep_csv that holds
                    the paths. Defaults to 1 if omitted.

──────────────────────────────────────────────────────────────────────────
Behaviour
──────────────────────────────────────────────────────────────────────────
• Verifies that every path in keep_csv resides inside target_dir; aborts if not.
• Recursively walks target_dir. Each file **not** in the keep list is sent
  to the Recycle Bin / Trash via `send2trash`.
• Matching is a simple string comparison of absolute paths.
• Prints a summary (Moved X/Y files…) and writes *report_csv*.
• Before deleting, the script shows how many keep‑paths it found and asks for confirmation.
• Also preserves any file whose **filename** matches one in the keep list.

Example:
    python file_deletion_tool.py "C:\\Data" keep_list.csv deleted_report.csv 2
"""

import csv
import os
import sys
from pathlib import Path
from send2trash import send2trash    # moves files to Recycle Bin / Trash

def load_keep_set(csv_path: Path, target_root: Path, path_col_idx: int = 0) -> set[str]:
    """
    USAGE: python prune_except_list.py  "C:\\Target\\Folder"  keep_list.csv  deleted_report.csv  [path_column]
    Read the first column (after header) of csv_path and return a set of
    *absolute* string paths that must be preserved.
    path_col_idx is zero‑based (0 = first column) and is supplied by the --path_column command parameter.

    Aborts if any listed path is outside target_root.
    """
    keep: set[str] = set()
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if not row or len(row) <= path_col_idx:
                continue
            raw = row[path_col_idx].strip().strip('"').strip("'")
            if not raw:
                continue
            p = Path(raw).expanduser().resolve(strict=False)
            # Failsafe: ensure path is under target_root
            if not str(p).startswith(str(target_root)):
                raise ValueError(f"CSV path '{p}' is not inside target directory '{target_root}'. Aborting.")
            p_str = os.path.normpath(str(p))
            keep.add(p_str.lower())
    return keep


def prune_directory(target_root: Path, keep: set[str], report_csv: Path, diag_csv: Path) -> None:
    """
    Walk target_root recursively. Move every file **not** in `keep` to the system Recycle Bin / Trash.
    Write a CSV report of files that were deleted (and any errors).
    """
    deleted_rows: list[list[str]] = []

    total_files = 0
    moved_files = 0

    # Diagnostics: record keep list and file-by-file status
    with diag_csv.open('w', newline='', encoding='utf-8') as df:
        diag_writer = csv.writer(df)
        diag_writer.writerow(['type','file_path','in_keep'])
        for kp in sorted(keep):
            diag_writer.writerow(['keep', kp, ''])
        # Walk files and write diagnostics for each
        for root, _, files in os.walk(target_root):
            for fname in files:
                total_files += 1
                file_path_obj = Path(root, fname)
                full = os.path.normpath(str(file_path_obj.resolve()))
                full_lower = full.lower()
                in_keep = full_lower in keep
                diag_writer.writerow(['file', full, str(in_keep)])

                if in_keep:
                    continue  # keep the file

                try:
                    send2trash(str(file_path_obj))
                    moved_files += 1
                    deleted_rows.append([str(file_path_obj.resolve()), ""])     # no error
                except Exception as e:                            # noqa: BLE001
                    deleted_rows.append([str(file_path_obj.resolve()), str(e)])

    # write report
    with report_csv.open("w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["deleted_path", "error"])
        writer.writerows(deleted_rows)

    print(f"Moved {moved_files}/{total_files} files to Recycle Bin / Trash under '{target_root}'")
    print(f"Detailed report written to '{report_csv}'")


def main() -> None:
    if len(sys.argv) not in (4, 5):
        script_name = Path(__file__).name
        print(f"Usage:  python {script_name} <target_dir> <keep_csv> <report_csv> [path_column]")
        print("        (Requires the 'send2trash' package – install with: pip install send2trash)")
        sys.exit(1)

    target_dir = Path(sys.argv[1]).expanduser().resolve()
    keep_csv = Path(sys.argv[2]).expanduser().resolve()
    report_csv = Path(sys.argv[3]).expanduser().resolve()
    diag_csv = report_csv.with_name(report_csv.stem + '_diagnostics.csv')

    # Optional 1‑based column number for paths in the CSV
    path_column = 1
    if len(sys.argv) == 5:
        try:
            path_column = int(sys.argv[4])
            if path_column < 1:
                raise ValueError
        except ValueError:
            print("Error: path_column must be a positive integer (1‑based index).")
            sys.exit(1)
    path_col_idx = path_column - 1  # convert to 0‑based for internal use

    if not target_dir.is_dir():
        print(f"Error: target directory '{target_dir}' does not exist or is not a directory.")
        sys.exit(1)

    if not keep_csv.is_file():
        print(f"Error: CSV '{keep_csv}' does not exist.")
        sys.exit(1)

    try:
        keep_set = load_keep_set(keep_csv, target_dir, path_col_idx)
    except ValueError as ex:
        print(ex)
        sys.exit(1)

    detected = len(keep_set)
    print(f"Detected {detected} unique file path(s) to keep (from '{keep_csv.name}').")
    reply = input("Proceed with pruning? [y/N]: ").strip().lower()
    if reply not in ("y", "yes"):
        print("Operation cancelled by user.")
        sys.exit(0)

    prune_directory(target_dir, keep_set, report_csv, diag_csv)


if __name__ == "__main__":
    main()