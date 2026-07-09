#!/usr/bin/env pwsh
# Run cosmic-ray mutation testing and generate TESTABLE metrics report.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot/..

Write-Host "==> Installing dependencies"
python -m pip install -e ".[dev]" -q

Write-Host "==> Running pytest baseline"
python -m pytest tests -q

Write-Host "==> Baseline (unmutated tests)"
cosmic-ray baseline cosmic-ray.toml

Write-Host "==> Initializing mutation session"
if (Test-Path session.sqlite) { Remove-Item session.sqlite -Force }
cosmic-ray init cosmic-ray.toml session.sqlite

Write-Host "==> Executing mutations (this may take several minutes)"
cosmic-ray exec cosmic-ray.toml session.sqlite

Write-Host "==> Generating TESTABLE metrics report"
python scripts/metrics_reporter.py --session session.sqlite --fail-on-gate

Write-Host "==> Cosmic Ray summary"
cr-rate session.sqlite
cr-report session.sqlite --surviving-only
