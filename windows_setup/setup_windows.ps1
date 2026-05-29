<#
Windows setup script for the repository.

Usage (PowerShell):
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  ./setup_windows.ps1 [-InstallDev]

Options:
  -InstallDev  Install dev extras (tests, linters).

#>

param(
    [switch]$InstallDev
)

function Abort($msg) {
    Write-Error $msg
    exit 1
}

Write-Host "Checking for Python..."
$py = & python --version 2>&1
if ($LASTEXITCODE -ne 0) { Abort "Python is not on PATH. Install Python 3.11+ and retry." }

if ($py -notmatch 'Python\s+(\d+)\.(\d+)') { Abort "Couldn't parse Python version: $py" }
$major = [int]$matches[1]
$minor = [int]$matches[2]
if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) { Abort "Python 3.11 or newer is required. Found: $py" }

Write-Host "Creating virtual environment .venv..."
& python -m venv .venv
if ($LASTEXITCODE -ne 0) { Abort "Failed to create virtual environment." }

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) { Write-Warning "Activation may have failed in this shell. Try: .\.venv\Scripts\Activate.ps1" }

Write-Host "Upgrading pip, setuptools, wheel..."
& python -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) { Abort "Failed to upgrade pip/setuptools/wheel." }

Write-Host "Installing project dependencies..."
if ($InstallDev) {
    & python -m pip install -e '.[dev]'
} else {
    & python -m pip install -e .
}
if ($LASTEXITCODE -ne 0) { Abort "Dependency installation failed." }

if (-not (Test-Path .env)) {
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Host "Created .env from .env.example — please review and update values."
    }
}

Write-Host "Done. To start using the environment run: .\\.venv\\Scripts\\Activate.ps1"
