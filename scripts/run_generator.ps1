$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    throw "Virtual environment not found. Run .\scripts\setup_local.ps1 first."
}

& ".\.venv\Scripts\Activate.ps1"

Write-Host "Generating synthetic batch data..."
python ".\ingestion\data_generator\generate_batch_data.py"

Write-Host ""
Write-Host "Validating generated data..."
python ".\ingestion\data_generator\validate_batch_data.py"
