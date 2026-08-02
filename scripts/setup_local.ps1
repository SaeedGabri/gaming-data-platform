$ErrorActionPreference = "Stop"

Write-Host "Creating local Python virtual environment..."

if (-not (Test-Path ".venv")) {
    py -m venv .venv
}

Write-Host "Activating environment..."
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Local setup complete."
Write-Host "No external Python packages are required for Phase 1."
