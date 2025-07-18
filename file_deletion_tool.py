#!/usr/bin/env python
import csv
import os
import sys
from pathlib import Path

def load_keep_set(csv_path: Path, target_root: Path) -> set[Path]:
    """
    USAGE: python prune_except_list.py  "C:\Target\Folder"  keep_list.csv  deleted_report.csv
    Read the first column (after header) of csv_path and return a set of
    *absolute, normalised* Path objects that must be preserved.

    Aborts if any listed path is outside target_root.
    """
    keep = set()

    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)                              # skip header
        for row in reader:
            if not row:
                continue
            raw = row[0].strip()
            if not raw:
                continue

            try:
                p = Path(raw).expanduser().resolve(strict=False)
            except (OSError, RuntimeError):
                # Malformed path – ignore it (nothing to preserve)
                continue

            # Failsafe: ensure p is inside target_root
            try:
                p.relative_to(target_root)
            except ValueError:
                raise ValueError(
                    f"CSV path '{p}' is not inside target directory '{target_root}'. "
                    "Aborting to protect your files."
                )
            keep.add(p)

    return keep


def prune_directory(target_root: Path, keep: set[Path], report_csv: Path) -> None:
    """
    Walk target_root recursively. Delete every file **not** in `keep`.
    Write a CSV report of files that were deleted (and any errors).
    """
    deleted_rows: list[list[str]] = []

    total_files = 0
    deleted_files = 0

    for root, _, files in os.walk(target_root):
        for fname in files:
            total_files += 1
            file_path = Path(root, fname).resolve()

            if file_path in keep:
                continue  # keep the file

            try:
                os.remove(file_path)
                deleted_files += 1
                deleted_rows.append([str(file_path), ""])     # no error
            except Exception as e:                            # noqa: BLE001
                deleted_rows.append([str(file_path), str(e)])

    # write report
    with report_csv.open("w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["deleted_path", "error"])
        writer.writerows(deleted_rows)

    print(f"Deleted {deleted_files}/{total_files} files under '{target_root}'")
    print(f"Detailed report written to '{report_csv}'")


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage:  python prune_except_list.py <target_dir> <keep_csv> <report_csv>")
        sys.exit(1)

    target_dir = Path(sys.argv[1]).expanduser().resolve()
    keep_csv = Path(sys.argv[2]).expanduser().resolve()
    report_csv = Path(sys.argv[3]).expanduser().resolve()

    if not target_dir.is_dir():
        print(f"Error: target directory '{target_dir}' does not exist or is not a directory.")
        sys.exit(1)

    if not keep_csv.is_file():
        print(f"Error: CSV '{keep_csv}' does not exist.")
        sys.exit(1)

    try:
        keep_set = load_keep_set(keep_csv, target_dir)
    except ValueError as ex:
        print(ex)
        sys.exit(1)

    prune_directory(target_dir, keep_set, report_csv)


if __name__ == "__main__":
    main()