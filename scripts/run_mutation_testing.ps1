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

Write-Host "==> Exporting dump and TESTABLE platform JSON"
New-Item -ItemType Directory -Force -Path cosmic-ray/0 | Out-Null
cosmic-ray dump session.sqlite > cosmic-ray/0/cosmic_ray_dump.jsonl

Write-Host "==> Generating TESTABLE metrics report"
python scripts/export_testable_cosmic_ray.py --fail-on-gate

Write-Host "==> Cosmic Ray summary"
cr-rate session.sqlite
cr-report session.sqlite --surviving-only
