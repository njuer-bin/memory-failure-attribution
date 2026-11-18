"""Analyze the Stage 2 LSF/SSF calibration.

Usage:
    G:/aconda/python.exe -m experiments.analyze_stage2_lsf_ssf
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from experiments.check_annotations import cohen_kappa

FIELDS = ["lsf_outcome", "ssf_outcome", "proposition_identity_in_memory",
          "status_assigned_from_memory"]
GATES = {
    "proposition_identity_in_memory": (0.90, 0.80),
    "lsf_outcome": (0.85, 0.70),
    "ssf_outcome": (0.80, 0.65),
}


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def compare(rows_a: list[dict], rows_b: list[dict], field: str) -> dict:
    pairs = []
    for row_a in rows_a:
        row_b = next(r for r in rows_b if r["memory_id"] == row_a["memory_id"])
        pairs.append(((row_a.get(field) or "").strip(),
                      (row_b.get(field) or "").strip()))
    a = [x for x, _ in pairs]
    b = [y for _, y in pairs]
    return {
        "n": len(pairs),
        "raw_agreement": sum(x == y for x, y in pairs) / len(pairs),
        "cohen_kappa": cohen_kappa(a, b),
        "A_distribution": dict(Counter(a)),
        "B_distribution": dict(Counter(b)),
        "disagreements": [
            {"memory_id": row["memory_id"], "A": x, "B": y}
            for row, (x, y) in zip(rows_a, pairs) if x != y
        ],
    }


def main() -> None:
    root = Path("results/status_drift_v3_real_audit/stage2_lsf_ssf")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", type=Path, default=root / "annotator_A.csv")
    parser.add_argument("--b", type=Path, default=root / "annotator_B.csv")
    parser.add_argument("--key", type=Path,
                        default=Path("G:/memory_failure_backup/stage2_lsf_ssf_key_2026-11-18.csv"))
    parser.add_argument("--out", type=Path, default=root / "analysis" / "agreement.json")
    args = parser.parse_args()

    rows_a, rows_b = load(args.a), load(args.b)
    if len(rows_a) != len(rows_b) or not rows_a:
        raise SystemExit(f"A/B row mismatch: A={len(rows_a)} B={len(rows_b)}")

    report = {"n_memories": len(rows_a), "fields": {}, "gates": {},
              "by_condition": {}}
    for field in FIELDS:
        report["fields"][field] = compare(rows_a, rows_b, field)
    for field, (raw_min, kappa_min) in GATES.items():
        item = report["fields"][field]
        report["gates"][field] = {
            "raw": item["raw_agreement"], "kappa": item["cohen_kappa"],
            "pass": item["raw_agreement"] >= raw_min
                    and (item["cohen_kappa"] or 0) >= kappa_min,
        }
    report["all_gates_pass"] = all(g["pass"] for g in report["gates"].values())

    if args.key.exists():
        with args.key.open(encoding="utf-8-sig", newline="") as handle:
            key = {row["memory_id"]: row for row in csv.DictReader(handle)}
        a_map = {row["memory_id"]: row for row in rows_a}
        b_map = {row["memory_id"]: row for row in rows_b}
        for memory_id, entry in key.items():
            condition = entry["condition"]
            bucket = report["by_condition"].setdefault(condition, {
                "n": 0, "A_lsf": Counter(), "B_lsf": Counter(),
                "A_ssf": Counter(), "B_ssf": Counter()})
            bucket["n"] += 1
            bucket["A_lsf"][a_map[memory_id]["lsf_outcome"]] += 1
            bucket["B_lsf"][b_map[memory_id]["lsf_outcome"]] += 1
            bucket["A_ssf"][a_map[memory_id]["ssf_outcome"]] += 1
            bucket["B_ssf"][b_map[memory_id]["ssf_outcome"]] += 1
        for bucket in report["by_condition"].values():
            for key_name in ("A_lsf", "B_lsf", "A_ssf", "B_ssf"):
                bucket[key_name] = dict(bucket[key_name])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    for field in FIELDS:
        item = report["fields"][field]
        print(f"{field}: raw={item['raw_agreement']:.3f} "
              f"kappa={item['cohen_kappa']} n={item['n']}")
    for field, gate in report["gates"].items():
        print(f"gate {field}: {gate['raw']:.3f}/{gate['kappa']} "
              f"{'PASS' if gate['pass'] else 'FAIL'}")
    print(f"ALL GATES: {'PASS' if report['all_gates_pass'] else 'FAIL'}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
