param(
    [string]$CondaEnv = "myenv",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$InitDatabase,
    [switch]$SkipMySQL,
    [switch]$SkipHealthCheck
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"
$frontendEnvFile = Join-Path $frontendDir ".env"
$condaExe = "D:/pysoft/anaconda/Scripts/conda.exe"

$mysqlMysqldExe = "D:/pysoft/mysql/mysql-8.4.8/mysql-8.4.8-winx64/bin/mysqld.exe"
$mysqlClientExe = "D:/pysoft/mysql/mysql-8.4.8/mysql-8.4.8-winx64/bin/mysql.exe"
$mysqlDefaultsFile = "D:/pysoft/mysql/instances/campus/conf/my.ini"
$dbInitSql = "D:/pyyolo/database/schema/init.sql"

if (-not (Test-Path $backendDir)) {
    throw "Missing backend directory: $backendDir"
}

if (-not (Test-Path $frontendDir)) {
    throw "Missing frontend directory: $frontendDir"
}

if (-not (Test-Path $condaExe)) {
    throw "Missing conda.exe: $condaExe"
}

if (-not (Test-Path $mysqlMysqldExe)) {
    throw "Missing mysqld.exe: $mysqlMysqldExe"
}

if ($InitDatabase -and -not (Test-Path $mysqlClientExe)) {
    throw "Missing mysql.exe: $mysqlClientExe"
}

if ($InitDatabase -and -not (Test-Path $dbInitSql)) {
    throw "Missing init sql: $dbInitSql"
}

if (-not (Test-Path $frontendEnvFile)) {
    "VITE_API_BASE_URL=http://127.0.0.1:$BackendPort/api/v1" | Set-Content -Path $frontendEnvFile -Encoding UTF8
    Write-Host "Created frontend env file: $frontendEnvFile"
}

if (-not $SkipMySQL) {
    $mysqlRunning = Get-Process mysqld -ErrorAction SilentlyContinue
    if ($mysqlRunning) {
        Write-Host "MySQL already running, skip starting a new instance."
    }
    else {
        $mysqlCommand = "& '$mysqlMysqldExe' --defaults-file='$mysqlDefaultsFile' --console"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $mysqlCommand | Out-Null
        Write-Host "Window A started: MySQL instance"
    }
}

if ($InitDatabase) {
    $dbInitCommand = "& '$mysqlClientExe' --user=root --password=123456 --host=127.0.0.1 --port=3306 -e 'source $dbInitSql'"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $dbInitCommand | Out-Null
    Write-Host "Window B started: Database init"
}

$backendCommand = @"
Set-Location '$backendDir'
& '$condaExe' run -n $CondaEnv python -m pip install --upgrade pip
& '$condaExe' run -n $CondaEnv python -m pip install -r '$backendDir\requirements.txt'
& '$condaExe' run -n $CondaEnv python -m uvicorn app.main:app --reload --reload-exclude='uploads/*' --reload-exclude='outputs/*' --reload-exclude='tools/*' --host 0.0.0.0 --port $BackendPort
"@

$frontendCommand = @"
Set-Location '$frontendDir'
if (-not (Test-Path '.env')) {
    Copy-Item .env.example .env -Force
}
npm install
npm run dev -- --host 0.0.0.0 --port $FrontendPort
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand | Out-Null
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand | Out-Null

function Test-Endpoint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,
        [int]$MaxSeconds = 60,
        [int]$IntervalSeconds = 2
    )

    $elapsed = 0
    while ($elapsed -lt $MaxSeconds) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        }
        catch {
        }

        Start-Sleep -Seconds $IntervalSeconds
        $elapsed += $IntervalSeconds
    }

    return $false
}

Write-Host "Window C started: Backend"
Write-Host "Window D started: Frontend"
Write-Host "Backend URL: http://127.0.0.1:$BackendPort"
Write-Host "Frontend URL: http://127.0.0.1:$FrontendPort"
Write-Host "Run command:"
Write-Host "  powershell -ExecutionPolicy Bypass -File tools/run_all.ps1"
Write-Host "First-time DB init:"
Write-Host "  powershell -ExecutionPolicy Bypass -File tools/run_all.ps1 -InitDatabase"
Write-Host "Skip MySQL window if already started:"
Write-Host "  powershell -ExecutionPolicy Bypass -File tools/run_all.ps1 -SkipMySQL"

if (-not $SkipHealthCheck) {
    Write-Host "Running health checks..."

    $backendRootOk = Test-Endpoint -Url "http://127.0.0.1:$BackendPort/" -MaxSeconds 120
    $dashboardOk = Test-Endpoint -Url "http://127.0.0.1:$BackendPort/api/v1/dashboard/stats" -MaxSeconds 30
    $tasksOk = Test-Endpoint -Url "http://127.0.0.1:$BackendPort/api/v1/tasks/" -MaxSeconds 30
    $frontendOk = Test-Endpoint -Url "http://127.0.0.1:$FrontendPort/" -MaxSeconds 120

    Write-Host "Health check result:"
    Write-Host "  backend root: $backendRootOk"
    Write-Host "  backend dashboard: $dashboardOk"
    Write-Host "  backend tasks: $tasksOk"
    Write-Host "  frontend root: $frontendOk"

    if (-not ($backendRootOk -and $dashboardOk -and $tasksOk -and $frontendOk)) {
        Write-Host "One or more checks failed. Please inspect the started terminal windows for error logs."
    }
}
