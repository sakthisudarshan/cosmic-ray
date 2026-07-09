#!/usr/bin/env python3
"""Compute TESTABLE Strategy Metrics from a Cosmic Ray mutation session.

Metrics mapping source: Testable_Strategy_Metrics_Mapping_v0.2 (White Box > Mutation Testing)
Tool: cosmic-ray (Python)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

BOUNDARY_OPERATOR_KEYWORDS = (
    "ReplaceComparisonOperator",
    "NumberReplacer",
    "ReplaceBinaryOperator",
    "Conditional",
    "boundary",
)


@dataclass
class MetricResult:
    metric_id: str
    primary_metric: str
    secondary_metric: str
    formula: str
    value: float
    score: float
    gate: str
    passed: bool
    details: dict[str, Any]


@dataclass
class MetricsReport:
    tool: str
    session_file: str
    total_mutants: int
    killed_mutants: int
    survived_mutants: int
    mutation_kill_rate_percent: float
    metrics: list[MetricResult]
    weak_spots: list[dict[str, Any]]
    module_kill_rates: dict[str, float]
    all_gates_passed: bool


def _is_boundary_operator(operator_name: str) -> bool:
    return any(keyword in operator_name for keyword in BOUNDARY_OPERATOR_KEYWORDS)


def _normalize_module(module_path: str) -> str:
    return Path(module_path.replace("\\", "/")).name


def load_session_records(session_file: Path) -> list[dict[str, Any]]:
    result = subprocess.run(
        ["cosmic-ray", "dump", str(session_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    records: list[dict[str, Any]] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if len(payload) != 2:
            continue
        work_item, work_result = payload
        if work_result is None:
            continue
        mutation = work_item["mutations"][0]
        records.append(
            {
                "job_id": work_item["job_id"],
                "module_path": mutation["module_path"],
                "module_name": _normalize_module(mutation["module_path"]),
                "operator_name": mutation["operator_name"],
                "occurrence": mutation["occurrence"],
                "definition_name": mutation.get("definition_name", ""),
                "test_outcome": work_result.get("test_outcome", "unknown"),
                "worker_outcome": work_result.get("worker_outcome", "unknown"),
                "is_boundary": _is_boundary_operator(mutation["operator_name"]),
            }
        )
    return records


def compute_metrics(records: list[dict[str, Any]], session_file: Path) -> MetricsReport:
    total = len(records)
    killed = sum(1 for record in records if record["test_outcome"] == "killed")
    survived = sum(1 for record in records if record["test_outcome"] == "survived")

    kill_rate = (killed / total) if total else 0.0

    by_module: dict[str, dict[str, int]] = defaultdict(lambda: {"killed": 0, "total": 0})
    for record in records:
        module_stats = by_module[record["module_name"]]
        module_stats["total"] += 1
        if record["test_outcome"] == "killed":
            module_stats["killed"] += 1

    module_kill_rates = {
        module: stats["killed"] / stats["total"] if stats["total"] else 0.0
        for module, stats in by_module.items()
    }
    weak_spot_modules = {
        module: rate for module, rate in module_kill_rates.items() if rate < 0.5
    }

    boundary_records = [record for record in records if record["is_boundary"]]
    boundary_total = len(boundary_records)
    boundary_killed = sum(
        1 for record in boundary_records if record["test_outcome"] == "killed"
    )
    boundary_kill_rate = (boundary_killed / boundary_total) if boundary_total else 0.0

    weak_spots = [
        {
            "module": record["module_name"],
            "function": record["definition_name"],
            "operator": record["operator_name"],
            "occurrence": record["occurrence"],
            "job_id": record["job_id"],
        }
        for record in records
        if record["test_outcome"] == "survived"
    ]

    metrics = [
        MetricResult(
            metric_id="M1",
            primary_metric="Fault Detection Capability",
            secondary_metric="Logic Error Sensitivity",
            formula="Logic Error Sensitivity = (total jobs - surviving mutants) / total jobs",
            value=kill_rate,
            score=kill_rate * 100,
            gate=">= 70%",
            passed=kill_rate >= 0.70,
            details={"killed": killed, "survived": survived, "total": total},
        ),
        MetricResult(
            metric_id="M2",
            primary_metric="Test Coverage Quality Validation",
            secondary_metric="Test Rigor Assessment",
            formula="Test Rigor = (total jobs - surviving mutants) / total jobs",
            value=kill_rate,
            score=kill_rate * 100,
            gate=">= 70%",
            passed=kill_rate >= 0.70,
            details={"killed": killed, "survived": survived, "total": total},
        ),
        MetricResult(
            metric_id="M3",
            primary_metric="Test Case Improvement Identification",
            secondary_metric="Weak Spot Localization",
            formula="Weak Spots = surviving mutants; Weak Spot Count = modules with kill rate < 50%",
            value=len(weak_spots) / total if total else 0.0,
            score=max(0.0, 100.0 - (len(weak_spot_modules) * 15)),
            gate="0 modules with mutation kill rate below 50%",
            passed=len(weak_spot_modules) == 0,
            details={
                "surviving_mutants": len(weak_spots),
                "weak_spot_module_count": len(weak_spot_modules),
                "weak_spot_modules": weak_spot_modules,
            },
        ),
        MetricResult(
            metric_id="M4",
            primary_metric="Edge Case Detection",
            secondary_metric="Boundary Mutant Analysis",
            formula="Boundary Kill Rate = boundary mutants killed / total boundary mutants",
            value=boundary_kill_rate,
            score=boundary_kill_rate * 100,
            gate=">= 80%",
            passed=boundary_kill_rate >= 0.80,
            details={
                "boundary_killed": boundary_killed,
                "boundary_total": boundary_total,
                "boundary_survived": boundary_total - boundary_killed,
            },
        ),
        MetricResult(
            metric_id="M5",
            primary_metric="Mutation Score",
            secondary_metric="Mutation Kill Rate %",
            formula="Mutation Kill Rate % = killed mutants / total mutants",
            value=kill_rate,
            score=kill_rate * 100,
            gate=">= 70%",
            passed=kill_rate >= 0.70,
            details={"killed": killed, "total": total},
        ),
    ]

    return MetricsReport(
        tool="cosmic-ray",
        session_file=str(session_file),
        total_mutants=total,
        killed_mutants=killed,
        survived_mutants=survived,
        mutation_kill_rate_percent=kill_rate * 100,
        metrics=metrics,
        weak_spots=weak_spots,
        module_kill_rates=module_kill_rates,
        all_gates_passed=all(metric.passed for metric in metrics),
    )


def render_markdown(report: MetricsReport) -> str:
    lines = [
        "# TESTABLE Mutation Testing Metrics Report",
        "",
        f"- **Tool:** {report.tool}",
        f"- **Session:** `{report.session_file}`",
        f"- **Mutation Kill Rate:** {report.mutation_kill_rate_percent:.2f}%",
        f"- **All Gates Passed:** {'YES' if report.all_gates_passed else 'NO'}",
        "",
        "## Metrics (from Strategy Mapping v0.2)",
        "",
        "| ID | Primary Metric | Secondary Metric | Score | Gate | Status |",
        "|----|----------------|------------------|-------|------|--------|",
    ]

    for metric in report.metrics:
        status = "PASS" if metric.passed else "FAIL"
        lines.append(
            f"| {metric.metric_id} | {metric.primary_metric} | "
            f"{metric.secondary_metric} | {metric.score:.2f}% | {metric.gate} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Module Kill Rates",
            "",
        ]
    )
    for module, rate in sorted(report.module_kill_rates.items()):
        lines.append(f"- `{module}`: {rate * 100:.2f}%")

    if report.weak_spots:
        lines.extend(["", "## Surviving Mutants (Weak Spots)", ""])
        for spot in report.weak_spots:
            lines.append(
                f"- `{spot['module']}::{spot['function']}` "
                f"({spot['operator']} #{spot['occurrence']})"
            )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--session",
        default="session.sqlite",
        help="Path to Cosmic Ray session SQLite file",
    )
    parser.add_argument(
        "--output-json",
        default="reports/metrics-report.json",
        help="Path for JSON metrics output",
    )
    parser.add_argument(
        "--output-md",
        default="reports/metrics-report.md",
        help="Path for Markdown metrics output",
    )
    parser.add_argument(
        "--fail-on-gate",
        action="store_true",
        help="Exit with code 1 when any metric gate fails",
    )
    args = parser.parse_args()

    session_file = Path(args.session)
    if not session_file.exists():
        print(f"Session file not found: {session_file}", file=sys.stderr)
        return 2

    records = load_session_records(session_file)
    report = compute_metrics(records, session_file)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    serializable = asdict(report)
    output_json.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")

    print(render_markdown(report))
    print(f"JSON report: {output_json}")
    print(f"Markdown report: {output_md}")

    if args.fail_on_gate and not report.all_gates_passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
