"""Check whether the Stage 2 60-item calibration sheets are complete.

Exits 0 only when both annotator sheets have 60 rows and all required gold
fields are filled (conditional rows also have both state fields). Prints status
to stderr so it can be used in a quiet polling loop.

Usage:
    G:/aconda/python.exe experiments/check_stage2_annotations.py
    G:/aconda/python.exe experiments/check_stage2_annotations.py \
        --dir results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi \
        --expected 40
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path("results/status_drift_v3_real_audit/stage2_calibration_60")
ESSENTIAL = [
    "target_proposition", "gold_dimension", "gold_status",
    "gold_strength", "gold_confidence", "evidence_quote",
]
CONDITIONAL = ["gold_condition_state", "gold_action_state"]


def check(path: Path, expected: int) -> tuple[bool, str]:
    if not path.exists():
        return False, f"{path.name}: missing"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != expected:
        return False, f"{path.name}: {len(rows)}/{expected} rows"
    missing = []
    for row in rows:
        for field in ESSENTIAL:
            if not (row.get(field) or "").strip():
                missing.append(f"{row['item_id']}:{field}")
        if (row.get("gold_dimension") or "").strip().lower() == "conditional":
            for field in CONDITIONAL:
                if not (row.get(field) or "").strip():
                    missing.append(f"{row['item_id']}:{field}")
    if missing:
        return False, f"{path.name}: {len(missing)} missing ({', '.join(missing[:4])}...)"
    return True, f"{path.name}: complete"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", type=Path, default=ROOT)
    parser.add_argument("--expected", type=int, default=60)
    args = parser.parse_args()
    results = [check(args.dir / "annotator_A.csv", args.expected),
               check(args.dir / "annotator_B.csv", args.expected)]
    for ok, message in results:
        print(message, file=sys.stderr)
    raise SystemExit(0 if all(ok for ok, _ in results) else 1)


if __name__ == "__main__":
    main()
