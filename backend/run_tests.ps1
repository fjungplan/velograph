#!/usr/bin/env pwsh
Set-Location "$PSScriptRoot"
Write-Host "Running full test suite..."
Write-Host "========================="
python -m pytest tests/ -v --tb=short 2>&1 | Select-Object -Last 100
