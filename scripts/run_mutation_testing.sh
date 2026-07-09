#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Installing dependencies"
python -m pip install -e ".[dev]" -q

echo "==> Running pytest baseline"
python -m pytest tests -q

echo "==> Baseline (unmutated tests)"
cosmic-ray baseline cosmic-ray.toml

echo "==> Initializing mutation session"
rm -f session.sqlite
cosmic-ray init cosmic-ray.toml session.sqlite

echo "==> Executing mutations (this may take several minutes)"
cosmic-ray exec cosmic-ray.toml session.sqlite

echo "==> Generating TESTABLE metrics report"
python scripts/metrics_reporter.py --session session.sqlite --fail-on-gate

echo "==> Cosmic Ray summary"
cr-rate session.sqlite
cr-report session.sqlite --surviving-only
