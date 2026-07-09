# TESTABLE Cosmic Ray — Mutation Testing Metrics Demo

Python mutation testing repository aligned with **Testable Strategy Metrics Mapping v0.2** (White Box → Mutation Testing). Uses [cosmic-ray](https://github.com/sixty-north/cosmic-ray) to measure mutation score and validate test suite effectiveness.

## Metrics Covered

| Primary Metric | Secondary Metric | Formula (Python / cosmic-ray) | Gate |
|----------------|------------------|--------------------------------|------|
| Fault Detection Capability | Logic Error Sensitivity | `(total jobs - surviving mutants) / total jobs` | ≥ 70% |
| Test Coverage Quality Validation | Test Rigor Assessment | `(total jobs - surviving mutants) / total jobs` | ≥ 70% |
| Test Case Improvement Identification | Weak Spot Localization | `surviving mutants`; modules with kill rate < 50% | 0 weak modules |
| Edge Case Detection | Boundary Mutant Analysis | `boundary mutants killed / total boundary mutants` | ≥ 80% |
| Mutation Score | Mutation Kill Rate % | `killed mutants / total mutants` | ≥ 70% |

Reference mapping: [`docs/Testable_Strategy_Metrics_Mapping_v0.2.xlsx`](docs/Testable_Strategy_Metrics_Mapping_v0.2.xlsx) (White Box sheet, rows 77–83).

## Quick Start

### Prerequisites

- Python 3.10+
- Git

### Install

```powershell
cd f:\Testable\cosmic-ray
python -m pip install -e ".[dev]"
```

### Run mutation testing + metrics (Windows)

```powershell
.\scripts\run_mutation_testing.ps1
```

### Run mutation testing + metrics (Linux/macOS)

```bash
chmod +x scripts/run_mutation_testing.sh
./scripts/run_mutation_testing.sh
```

### Manual step-by-step

```powershell
python -m pytest tests -q
cosmic-ray baseline cosmic-ray.toml
cosmic-ray init cosmic-ray.toml session.sqlite
cosmic-ray exec cosmic-ray.toml session.sqlite
python scripts/metrics_reporter.py --session session.sqlite --fail-on-gate
cr-rate session.sqlite
cr-report session.sqlite --surviving-only
```

## Output

After a run, reports are written to:

- `reports/metrics-report.json` — machine-readable metrics for CI/integration
- `reports/metrics-report.md` — human-readable summary with gate pass/fail

## Project Layout

```
src/testable_demo/     # Code under test (calculator, order validation, discounts)
tests/                 # Pytest suite designed for high mutation kill rate
cosmic-ray.toml        # Cosmic Ray configuration
scripts/
  metrics_reporter.py  # Maps session results → TESTABLE metrics
  run_mutation_testing.ps1 / .sh
docs/
  Testable_Strategy_Metrics_Mapping_v0.2.xlsx
.github/workflows/mutation-testing.yml
```

## GitHub CI

Push to `main` triggers GitHub Actions mutation testing. Artifacts include JSON and Markdown metric reports for manual validation.

**Remote:** https://github.com/sakthisudarshan/cosmic-ray

## Manual Validation Checklist

1. Clone the repo and run `.\scripts\run_mutation_testing.ps1`
2. Open `reports/metrics-report.md` and confirm all gates show **PASS**
3. Review surviving mutants in the report (weak spots to improve tests)
4. Compare metric formulas against the Excel mapping (White Box → Mutation Testing)
5. Push a change and verify the GitHub Actions workflow completes with green status

## Improving Weak Spots

If gates fail, inspect surviving mutants:

```powershell
cr-report session.sqlite --surviving-only --show-diff
```

Add targeted assertions in `tests/` for boundary conditions and comparison operators, then re-run.

## License

MIT — demo project for TESTABLE metrics validation.
