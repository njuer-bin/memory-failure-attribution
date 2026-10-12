"""Post-hoc audit for lifecycle failure attribution.

F4 is defined as a retrieval OR rerank failure.  The audit must therefore
accept either stage as the blocking lifecycle loss and only warn when neither
stage is missing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


F4_WARNING = "F4_WITHOUT_RETRIEVAL_OR_RERANK_LOSS"


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("_status", "ok") == "ok":
                rows.append(row)
    return rows


def _stage_status(real: dict[str, Any], stage: str) -> str:
    data = real.get(stage) or {}
    if data.get("found"):
        return "FOUND"
    if data.get("missing"):
        return "MISSING"
    return "UNKNOWN"


def audit_row(row: dict[str, Any]) -> list[str]:
    """Return attribution audit warnings for one experiment row."""
    real = row.get("modes", {}).get("real_memory", {})
    answer_failure = real.get("answer_failure_type")
    issues: list[str] = []

    if answer_failure == "F4_RETRIEVAL":
        retrieval = _stage_status(real, "retrieval")
        rerank = _stage_status(real, "rerank")
        if retrieval != "MISSING" and rerank != "MISSING":
            issues.append(F4_WARNING)

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit lifecycle failure attributions")
    parser.add_argument(
        "--input",
        default="results/oracle_experiments/comparison.jsonl",
        help="Path to comparison.jsonl",
    )
    args = parser.parse_args()

    rows = load_rows(Path(args.input))
    warning_count = 0
    for row in rows:
        issues = audit_row(row)
        if issues:
            warning_count += len(issues)
            print(row.get("question_id", "<unknown>"))
            for issue in issues:
                print(f"  - {issue}")

    print(f"Audited rows: {len(rows)}")
    print(f"Warnings: {warning_count}")


if __name__ == "__main__":
    main()
