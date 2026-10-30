$ErrorActionPreference = "Stop"

$docsUrl = "http://127.0.0.1:8000/"
$chromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LocalAppData}\Google\Chrome\Application\chrome.exe"
)
$chrome = $chromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $chrome) {
    throw "Google Chrome was not found. Install Chrome and try again."
}

try {
    Invoke-WebRequest -UseBasicParsing -Uri $docsUrl -TimeoutSec 2 | Out-Null
    throw "A documentation server is already using port 8000. Stop it before running this launcher."
}
catch [System.Net.WebException] {
    # The port is available, so this launcher can own the server process.
}

$mkdocs = Get-Command mkdocs.exe -ErrorAction SilentlyContinue
if ($mkdocs) {
    $server = Start-Process -FilePath $mkdocs.Source -ArgumentList "serve" -WorkingDirectory $PSScriptRoot -PassThru
}
else {
    & python -m mkdocs --version *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "MkDocs Material is not installed. Run: pip install mkdocs-material"
    }

    $server = Start-Process -FilePath "python" -ArgumentList "-m", "mkdocs", "serve" -WorkingDirectory $PSScriptRoot -PassThru
}

$chromeProfile = Join-Path ([System.IO.Path]::GetTempPath()) "tzamot-docs-chrome-$PID"

try {
    Write-Host "Waiting for the documentation server..."
    $ready = $false

    foreach ($attempt in 1..30) {
        if ($server.HasExited) {
            throw "The documentation server exited with code $($server.ExitCode)."
        }

        try {
            Invoke-WebRequest -UseBasicParsing -Uri $docsUrl -TimeoutSec 1 | Out-Null
            $ready = $true
            break
        }
        catch [System.Net.WebException] {
            Start-Sleep -Seconds 1
        }
    }

    if (-not $ready) {
        throw "The documentation server did not start within 30 seconds."
    }

    $chromeArguments = @(
        "--user-data-dir=`"$chromeProfile`""
        "--app=$docsUrl"
        "--disable-background-mode"
        "--no-first-run"
    )

    Write-Host "Close the Chrome documentation window to stop the server."
    $chromeProcess = Start-Process -FilePath $chrome -ArgumentList $chromeArguments -PassThru
    $chromeProcess.WaitForExit()
}
finally {
    if ($server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id
        $server.WaitForExit()
    }

    if (Test-Path $chromeProfile) {
        Remove-Item -Path $chromeProfile -Recurse -Force
    }
}
