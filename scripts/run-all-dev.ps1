# Launches the full microservices stack locally, each in its own window.
#
# Self-manages a Python virtualenv OUTSIDE the OneDrive-synced project tree
# (default: %USERPROFILE%\tra-venv). This avoids the recurring problem where a
# venv created inside the OneDrive folder breaks when synced across machines or
# when its base interpreter moves. Every service's dependencies are a subset of
# the gateway's, so a single venv runs the whole stack.
#
# Usage:
#   ./scripts/run-all-dev.ps1            # create venv if missing, then run
#   ./scripts/run-all-dev.ps1 -Setup     # force (re)install dependencies
#   ./scripts/run-all-dev.ps1 -VenvDir D:\envs\tra   # custom venv location

param(
    [string]$VenvDir = (Join-Path $env:USERPROFILE "tra-venv"),
    [switch]$Setup
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$gwDir = Join-Path $root "apps\api-gateway"
$venvPython = Join-Path $VenvDir "Scripts\python.exe"

function Resolve-BasePython {
    # Prefer the py launcher (selects a real install, not the WindowsApps stub).
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return @{ Exe = $py.Source; Args = @("-3") } }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python -and $python.Source -notlike "*WindowsApps*") {
        return @{ Exe = $python.Source; Args = @() }
    }
    throw "No suitable Python found. Install Python 3.11+ and ensure 'py' or 'python' is on PATH."
}

# Create the venv outside OneDrive if it is missing.
if (-not (Test-Path $venvPython)) {
    $base = Resolve-BasePython
    Write-Host "Creating venv at $VenvDir using $($base.Exe) $($base.Args)"
    & $base.Exe @($base.Args + @("-m", "venv", $VenvDir))
    $Setup = $true
}

# Install dependencies on first creation or when -Setup is passed.
if ($Setup) {
    Write-Host "Installing dependencies into $VenvDir ..."
    & $venvPython -m pip install --upgrade pip
    Push-Location $gwDir
    try {
        & $venvPython -m pip install -e ".[dev]"
    } finally {
        Pop-Location
    }
    # parser-service and reporting-service need these; trimmed from the gateway.
    & $venvPython -m pip install "python-hcl2>=4.3.3" "jinja2>=3.1.4"
}

Write-Host "Using interpreter: $venvPython"
Write-Host ""

function Start-Svc($name, $port, $prelude) {
    $dir = Join-Path $root "apps\$name"
    $cmd = "Set-Location '$dir'; $prelude& '$venvPython' -m uvicorn app.main:app --host 127.0.0.1 --port $port --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
    Write-Host "Started $name -> http://127.0.0.1:$port"
}

Start-Svc "upload-service"    8001 "`$env:STORAGE_PATH='./data/storage'; "
Start-Svc "parser-service"    8002 ""
Start-Svc "rules-service"     8003 ""
Start-Svc "ai-review-service" 8004 ""
Start-Svc "scoring-service"   8005 ""
Start-Svc "reporting-service" 8006 ""

# Gateway last: seed the admin user, then serve.
$gwCmd = "Set-Location '$gwDir'; & '$venvPython' -m app.bootstrap; & '$venvPython' -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $gwCmd
Write-Host "Started api-gateway -> http://127.0.0.1:8000 (docs at /docs)"
Write-Host ""
Write-Host "Frontend: cd apps/frontend; npm install; npm run dev  -> http://localhost:5173"
