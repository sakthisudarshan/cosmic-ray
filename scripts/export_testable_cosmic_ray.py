#!/usr/bin/env python3
"""Post-process cosmic-ray output for the TESTABLE platform.

Run after cosmic-ray exec in CI or locally. Writes cosmic-ray/0/cosmic_ray.json
with embedded 0-100 metrics so the taxonomy gate reads correct scores.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.metrics_reporter import (  # noqa: E402
    build_platform_cosmic_ray_json,
    build_testable_gate_report,
    compute_metrics,
    load_session_records,
)


def main() -> int:
    fail_on_gate = "--fail-on-gate" in sys.argv
    session = ROOT / "session.sqlite"
    out_dir = ROOT / "cosmic-ray" / "0"
    dump_file = out_dir / "cosmic_ray_dump.jsonl"
    platform_file = out_dir / "cosmic_ray.json"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not session.exists():
        print(f"Missing session: {session}", file=sys.stderr)
        return 2

    try:
        dump_text = subprocess.check_output(
            ["cosmic-ray", "dump", str(session)],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        dump_file.write_text(dump_text, encoding="utf-8")
    except subprocess.CalledProcessError as exc:
        print(f"cosmic-ray dump failed: {exc}", file=sys.stderr)
        return exc.returncode or 1

    records = load_session_records(session)
    report = compute_metrics(records, session)
    gate_report = build_testable_gate_report(report)
    platform_report = build_platform_cosmic_ray_json(
        session,
        gate_report,
        report,
        dump_path="cosmic-ray/0/cosmic_ray_dump.jsonl",
    )

    (ROOT / "reports").mkdir(parents=True, exist_ok=True)
    (ROOT / "reports" / "mutation-score-gate.json").write_text(
        json.dumps(gate_report, indent=2),
        encoding="utf-8",
    )
    platform_file.write_text(json.dumps(platform_report, indent=2), encoding="utf-8")

    print(f"Mutation Kill Rate: {report.mutation_kill_rate_percent:.2f}%")
    print(f"All Gates Passed: {'YES' if report.all_gates_passed else 'NO'}")
    print(f"Platform cosmic_ray.json: {platform_file}")

    if fail_on_gate and not report.all_gates_passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
