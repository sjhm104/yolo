param(
    [int]$KeepHours = 24,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$targets = @(
    (Join-Path $projectRoot "backend/uploads/videos"),
    (Join-Path $projectRoot "backend/outputs/videos")
)

$expireBefore = (Get-Date).AddHours(-1 * $KeepHours)

Write-Host "Cleaning media files older than $KeepHours hours..."
Write-Host "Expire before: $expireBefore"

foreach ($dir in $targets) {
    if (-not (Test-Path $dir)) {
        Write-Host "Skip missing directory: $dir"
        continue
    }

    $files = Get-ChildItem -Path $dir -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -ne ".gitkeep" -and
            $_.LastWriteTime -lt $expireBefore
        }

    if (-not $files) {
        Write-Host "No expired files in: $dir"
        continue
    }

    foreach ($file in $files) {
        if ($WhatIf) {
            Write-Host "[WhatIf] Remove: $($file.FullName)"
        }
        else {
            Remove-Item -Path $file.FullName -Force
            Write-Host "Removed: $($file.FullName)"
        }
    }
}

Write-Host "Done"
