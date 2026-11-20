"""Build blank two-human validation sheets for the 16 expansion controls.

The original 40 scenarios have `results/status_drift_v3_p4_2/validation_{A,B}.csv`.
The 16 controls added for precision (`*-11`..`*-14`) never got human sheets.
This writes `validation_A_16.csv` and `validation_B_16.csv` with the same
columns and no ratings, so two annotators can fill them and then run
`experiments.check_p4_2_validation --a ..._A_16.csv --b ..._B_16.csv`.

The two sheets are shuffled independently (fixed seeds) to reduce order
effects; the checker joins on `scenario_id`, so order is irrelevant to scoring.
Gold status, expected decision, and control type are deliberately omitted.

Usage:
    G:/aconda/python.exe -m experiments.make_validation_sheets_16
"""

from __future__ import annotations

import argparse
import csv
import random
import re
from pathlib import Path

import yaml

COLUMNS = [
    "scenario_id", "domain", "title", "evidence", "rule", "request",
    "present", "omitted", "distorted",
    "realism_1_5", "status_clarity_1_5", "rule_clarity_1_5",
    "only_status_differs", "distortion_plausible_1_5", "stake_severity_1_5",
    "notes",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path,
                        default=Path("datasets/p4_2_scenarios/p4_2_scenarios.yaml"))
    parser.add_argument("--out-dir", type=Path,
                        default=Path("results/status_drift_v3_p4_2"))
    parser.add_argument("--id-regex", default=r"-(1[1-4])$")
    args = parser.parse_args()

    data = yaml.safe_load(args.bank.read_text(encoding="utf-8"))
    pattern = re.compile(args.id_regex)
    scenarios = [s for s in data["scenarios"] if pattern.search(s["id"])]
    if len(scenarios) != 16:
        raise SystemExit(f"expected 16 controls, found {len(scenarios)}")

    rows = []
    for s in scenarios:
        rows.append({
            "scenario_id": s["id"],
            "domain": s.get("domain", ""),
            "title": s.get("title", ""),
            "evidence": s.get("evidence", ""),
            "rule": s.get("rule", ""),
            "request": s.get("request", ""),
            "present": s["variants"]["present"],
            "omitted": s["variants"]["omitted"],
            "distorted": s["variants"]["distorted"],
            # rating columns left blank for the annotators
            "realism_1_5": "",
            "status_clarity_1_5": "",
            "rule_clarity_1_5": "",
            "only_status_differs": "",
            "distortion_plausible_1_5": "",
            "stake_severity_1_5": "",
            "notes": "",
        })

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, seed in (("A", 20261120), ("B", 20261121)):
        shuffled = rows[:]
        random.Random(seed).shuffle(shuffled)
        path = args.out_dir / f"validation_{name}_16.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(shuffled)
        print(f"wrote {path} ({len(shuffled)} rows)")


if __name__ == "__main__":
    main()
