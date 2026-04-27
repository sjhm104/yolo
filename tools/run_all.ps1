param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$InitDatabase,
    [switch]$SkipMySQL
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"
$venvDir = Join-Path $projectRoot ".venv"
$frontendEnvFile = Join-Path $frontendDir ".env"

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
    $mysqlCommand = "& '$mysqlMysqldExe' --defaults-file='$mysqlDefaultsFile' --console"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $mysqlCommand | Out-Null
    Write-Host "Window A started: MySQL instance"
}

if ($InitDatabase) {
    $dbInitCommand = "& '$mysqlClientExe' --user=root --password=123456 --host=127.0.0.1 --port=3306 -e 'source $dbInitSql'"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $dbInitCommand | Out-Null
    Write-Host "Window B started: Database init"
}

$backendCommand = @"
Set-Location '$projectRoot'
python -m venv .venv
& '$venvDir\Scripts\Activate.ps1'
python -m pip install --upgrade pip
python -m pip install -r '$backendDir\requirements.txt'
Set-Location '$backendDir'
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BackendPort
"@

$frontendCommand = @"
Set-Location '$frontendDir'
Copy-Item .env.example .env -Force
npm install
npm run dev -- --host 0.0.0.0 --port $FrontendPort
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand | Out-Null
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand | Out-Null

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
