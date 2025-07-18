

<#
.SYNOPSIS
  Prunes a directory by moving all files except those listed in a CSV into the Recycle Bin.

.DESCRIPTION
  Reads a CSV of file paths to keep, verifies each is under the target directory,
  then recursively scans the target directory and moves any file not in the keep list
  into the Windows Recycle Bin. At the end, writes a report CSV of moved files and any errors.

  Requires PowerShell 7 and .NET’s Microsoft.VisualBasic assembly for Recycle Bin operations.

.PARAMETER TargetDir
  The root directory whose files will be pruned.

.PARAMETER KeepCsv
  Path to a CSV file (with header row) containing file paths to retain.
  The CSV column to use is indicated by PathColumn (1-based).

.PARAMETER ReportCsv
  Path to write the report CSV listing moved files and error messages.

.PARAMETER PathColumn
  (Optional) 1-based index of the column in KeepCsv containing the file paths. Defaults to 1.

.EXAMPLE
  PS> .\file_deletion_tool.ps1 -TargetDir 'C:\Data' -KeepCsv 'keep.csv' `
       -ReportCsv 'deleted_report.csv' -PathColumn 2
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$TargetDir,

    [Parameter(Mandatory)]
    [string]$KeepCsv,

    [Parameter(Mandatory)]
    [string]$ReportCsv,

    [int]$PathColumn = 1
)

# Load VisualBasic assembly for Recycle Bin support
Add-Type -AssemblyName Microsoft.VisualBasic

# Resolve and normalize target directory
$targetRoot = (Get-Item -LiteralPath $TargetDir).FullName

# Read and verify keep list
Write-Host "Loading keep list from '$KeepCsv' (column $PathColumn)..."
try {
    $csv = Import-Csv -Path $KeepCsv -ErrorAction Stop
} catch {
    Write-Error "Failed to read CSV: $_"
    exit 1
}

$keepSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($row in $csv) {
    $values = $row.PSObject.Properties.Value
    if ($values.Count -lt $PathColumn) { continue }
    $raw = $values[$PathColumn - 1].Trim(" `""'" )
    if ([string]::IsNullOrWhiteSpace($raw)) { continue }
    try {
        $full = (Get-Item -LiteralPath $raw -ErrorAction Stop).FullName
    } catch {
        Write-Warning "Skipping invalid path: $raw"
        continue
    }
    if (-not $full.StartsWith($targetRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Error "CSV path '$full' is not under target directory '$targetRoot'. Aborting."
        exit 1
    }
    $keepSet.Add($full) | Out-Null
}

Write-Host "Will preserve $($keepSet.Count) file(s)."

# Prepare report list
$report = [System.Collections.Generic.List[PSObject]]::new()

# Walk target directory and move files not in keepSet
Write-Host "Pruning files under '$targetRoot'..."
$allFiles = Get-ChildItem -LiteralPath $targetRoot -File -Recurse -ErrorAction Stop
$total = $allFiles.Count
$moved = 0

foreach ($file in $allFiles) {
    $path = $file.FullName
    if ($keepSet.Contains($path)) {
        continue
    }
    try {
        [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile(
            $path,
            [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
            [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin
        )
        $moved++
        $report.Add([PSCustomObject]@{ DeletedPath = $path; Error = '' })
    } catch {
        $report.Add([PSCustomObject]@{ DeletedPath = $path; Error = $_.Exception.Message })
    }
}

# Write report CSV
$report | Export-Csv -Path $ReportCsv -NoTypeInformation -Encoding UTF8

Write-Host "Moved $moved/$total files to Recycle Bin. Report at '$ReportCsv'."