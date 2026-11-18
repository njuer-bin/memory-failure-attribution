"""Check whether the Stage 2 LSF/SSF calibration sheets are complete.

Exits 0 only when both annotator sheets have 45 rows and the four required
fields are filled. Prints status to stderr.

Usage:
    G:/aconda/python.exe experiments/check_stage2_lsf_ssf.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path("results/status_drift_v3_real_audit/stage2_lsf_ssf")
FIELDS = ["lsf_outcome", "ssf_outcome", "status_assigned_from_memory",
          "proposition_identity_in_memory"]


def check(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, f"{path.name}: missing"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 45:
        return False, f"{path.name}: {len(rows)}/45 rows"
    missing = [(row["memory_id"], field) for row in rows for field in FIELDS
               if not (row.get(field) or "").strip()]
    if missing:
        return False, f"{path.name}: {len(missing)} missing ({missing[:3]}...)"
    return True, f"{path.name}: complete"


def main() -> None:
    results = [check(ROOT / "annotator_A.csv"), check(ROOT / "annotator_B.csv")]
    for ok, message in results:
        print(message, file=sys.stderr)
    raise SystemExit(0 if all(ok for ok, _ in results) else 1)


if __name__ == "__main__":
    main()
