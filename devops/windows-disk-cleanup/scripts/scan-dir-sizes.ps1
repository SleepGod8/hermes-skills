# scan-dir-sizes.ps1  --  read-only, fast, junction-safe directory sizing
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File .\scan-dir-sizes.ps1 -Root 'D:/' -Out 'C:\tmp\out.csv' [-Top 40]
# Rules baked in (see SKILL.md):
#   * robocopy list mode, /XJ skips junctions -> no infinite recursion, seconds for hundreds of GB
#   * keep job summary (/NJH only). Adding /NJS removes the 'Bytes :' line -> every size becomes 0
#   * ASCII-only source: PowerShell 5.1 reads BOM-less .ps1 as GBK and Chinese literals break parsing
#   * always pass -Root with FORWARD slashes in single quotes ('D:/'), never 'D:\' (bash eats the quote)
param([string]$Root,[string]$Out,[int]$Top=50)
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$ErrorActionPreference = 'SilentlyContinue'

function Get-DirSizeGB {
    param([string]$p)
    $bytes = 0
    $out = & robocopy $p 'NULL' /L /S /NJH /BYTES /NFL /NDL /XJ /R:0 /W:0 2>$null
    foreach ($line in $out) {
        if ($line -match '^\s*Bytes\s*:\s+(\d+)') { $bytes = [int64]$matches[1]; break }
    }
    return [math]::Round($bytes / 1GB, 2)
}

$rows = @()
$dirs = Get-ChildItem -LiteralPath $Root -Directory -Force -ErrorAction SilentlyContinue
foreach ($d in $dirs) {
    $gb = Get-DirSizeGB $d.FullName
    $i = Get-Item -LiteralPath $d.FullName -Force -ErrorAction SilentlyContinue
    $lw = ''
    if ($i) { $lw = $i.LastWriteTime.ToString('yyyy-MM-dd') }
    $rows += [PSCustomObject]@{ Path = $d.FullName; GB = $gb; LastWrite = $lw }
}

$files = Get-ChildItem -LiteralPath $Root -File -Force -ErrorAction SilentlyContinue
if ($files) {
    $s = ($files | Measure-Object -Property Length -Sum).Sum
    if (-not $s) { $s = 0 }
    $rows += [PSCustomObject]@{ Path = "$Root<root loose files>"; GB = [math]::Round($s/1GB,2); LastWrite = '' }
}

$rows | Sort-Object GB -Descending | Select-Object -First $Top |
    Export-Csv -LiteralPath $Out -NoTypeInformation -Encoding UTF8

if (-not (Test-Path -LiteralPath $Out)) { Write-Output "ERROR: csv not written, check -Out directory: $Out"; exit 1 }
Write-Output "DONE $Out dirs=$($dirs.Count) totalGB=$([math]::Round(($rows | Measure-Object -Property GB -Sum).Sum,2))"
