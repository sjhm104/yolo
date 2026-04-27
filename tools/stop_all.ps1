param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$StopMySQL
)

$ErrorActionPreference = "Stop"

$mysqlAdminExe = "D:/pysoft/mysql/mysql-8.4.8/mysql-8.4.8-winx64/bin/mysqladmin.exe"

function Stop-ProcessByPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        Write-Host "$Name not running on port $Port"
        return
    }

    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Host "Stopped $Name process PID=$pid on port $Port"
        }
        catch {
            Write-Host "Failed to stop $Name process PID=${pid}: $($_.Exception.Message)"
        }
    }
}

Stop-ProcessByPort -Port $BackendPort -Name "Backend"
Stop-ProcessByPort -Port $FrontendPort -Name "Frontend"

if ($StopMySQL) {
    if (Test-Path $mysqlAdminExe) {
        try {
            & $mysqlAdminExe --user=root --password=123456 --host=127.0.0.1 --port=3306 shutdown
            Write-Host "MySQL shutdown command sent"
        }
        catch {
            Write-Host "Failed to shutdown MySQL gracefully: $($_.Exception.Message)"
        }
    }
    else {
        Write-Host "mysqladmin not found at: $mysqlAdminExe"
    }
}

Write-Host "Done"
