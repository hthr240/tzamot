#Requires -Version 5.1
$ErrorActionPreference = "Stop"

# PowerShell variable names are case-insensitive, so keep path and process
# names distinct (Frontend vs frontend would collide).
$Root = $PSScriptRoot
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$Seed = $false

foreach ($arg in $args) {
    switch -Regex ($arg) {
        "^--seed$" { $Seed = $true }
        "^(-h|--help)$" {
            Write-Host @"
Usage: .\dev-up.cmd [--seed]

Starts PostgreSQL, applies migrations, then runs the API on :8000 and the
frontend on :5500. Press Ctrl+C to stop the API and frontend. The database
keeps running and keeps its data (use ``docker compose down`` to stop it).

  --seed   Run scripts/seed_test_db.py after migrations
"@
            exit 0
        }
        default { throw "Unknown argument: $arg. Use --help." }
    }
}

function Test-LocalPortInUse([int]$Port) {
    try {
        $client = [System.Net.Sockets.TcpClient]::new()
        $client.Connect("127.0.0.1", $Port)
        $client.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Assert-PortFree([int]$Port, [string]$Owner) {
    if (Test-LocalPortInUse $Port) {
        throw "Port $Port is already in use. Stop the process using it before starting $Owner."
    }
}

function Require-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found. $Hint"
    }
}

Require-Command "docker" "Install Docker Desktop and make sure it is running."
Require-Command "uv" "Install uv: https://docs.astral.sh/uv/getting-started/installation/"

$pythonLauncher = $null
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonLauncher = @("py", "-3")
}
elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonLauncher = @("python")
}
else {
    throw "Python was not found. Install Python 3.13 or the Windows py launcher."
}

Assert-PortFree 8000 "the API (uvicorn)"
Assert-PortFree 5500 "the frontend static server"

Write-Host "Starting PostgreSQL..."
& docker compose up -d --wait
if ($LASTEXITCODE -ne 0) {
    throw "docker compose failed with exit code $LASTEXITCODE. Is Docker Desktop running?"
}

Write-Host "Applying migrations..."
Push-Location $BackendDir
try {
    & uv run alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        throw "alembic upgrade head failed with exit code $LASTEXITCODE."
    }

    if ($Seed) {
        Write-Host "Seeding the database..."
        & uv run python -m scripts.seed_test_db
        if ($LASTEXITCODE -ne 0) {
            throw "seed_test_db failed with exit code $LASTEXITCODE."
        }
    }
}
finally {
    Pop-Location
}

$apiProcess = $null
$frontendProcess = $null

try {
    Write-Host "Starting API on http://127.0.0.1:8000 ..."
    $apiProcess = Start-Process -FilePath "uv" -ArgumentList @(
        "run", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"
    ) -WorkingDirectory $BackendDir -PassThru -NoNewWindow

    Write-Host "Starting frontend on http://127.0.0.1:5500 ..."
    if ($pythonLauncher[0] -eq "py") {
        $frontendProcess = Start-Process -FilePath "py" -ArgumentList @(
            "-3", "-m", "http.server", "5500", "--bind", "127.0.0.1"
        ) -WorkingDirectory $FrontendDir -PassThru -NoNewWindow
    }
    else {
        $frontendProcess = Start-Process -FilePath "python" -ArgumentList @(
            "-m", "http.server", "5500", "--bind", "127.0.0.1"
        ) -WorkingDirectory $FrontendDir -PassThru -NoNewWindow
    }

    Write-Host ""
    Write-Host "Local stack is up."
    Write-Host "  API       http://127.0.0.1:8000/health"
    Write-Host "  Frontend  http://127.0.0.1:5500/"
    Write-Host "  Docs API  http://127.0.0.1:8000/docs"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the API and frontend."
    Write-Host "The database stays up. Stop it with: docker compose down"
    Write-Host ""

    while ($true) {
        if ($apiProcess.HasExited) {
            throw "The API process exited with code $($apiProcess.ExitCode)."
        }
        if ($frontendProcess.HasExited) {
            throw "The frontend process exited with code $($frontendProcess.ExitCode)."
        }
        Start-Sleep -Seconds 1
    }
}
finally {
    foreach ($process in @($frontendProcess, $apiProcess)) {
        if ($null -eq $process) {
            continue
        }
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            try {
                $process.WaitForExit(5000) | Out-Null
            }
            catch {
                # Process may already be gone.
            }
        }
    }
    Write-Host "API and frontend stopped. Database is still running."
}
