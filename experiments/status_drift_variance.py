"""Repeated-run variance analysis for status-drift records.

Compares memory identity and deterministic status metrics across runs.
Usage:
    python -m experiments.status_drift_variance <dir> <dir> [<dir> ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from evaluation.status_cue_metrics import summarize_records

DEPTHS = ("1", "2", "3", "5")
KINDS = ("direct", "recursive", "rewrite_matched")


def load_records(directory: str | Path) -> dict[str, dict]:
    rows = {}
    for line in (Path(directory) / "records.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["sample_id"]] = row
    return rows


def memory_identity(a: dict[str, dict], b: dict[str, dict]) -> dict[str, dict]:
    result = {}
    common = sorted(set(a) & set(b))
    for kind in KINDS:
        for depth in DEPTHS:
            identical = total = 0
            for sid in common:
                ma = (a[sid].get(f"{kind}_memories") or {}).get(depth)
                mb = (b[sid].get(f"{kind}_memories") or {}).get(depth)
                if ma is None or mb is None:
                    continue
                total += 1
                if ma == mb:
                    identical += 1
            if total:
                result[f"{kind}_d{depth}"] = {
                    "identical": identical, "total": total, "rate": identical / total,
                }
    return result


def condition_omission(directory: str | Path) -> dict[str, dict]:
    from experiments.status_drift_recursive_pilot import (
        TOPIC_KEYWORDS,
        det_condition_status,
    )
    rows = load_records(directory)
    result = {}
    for kind in KINDS:
        for depth in DEPTHS:
            tot = om = 0
            for row in rows.values():
                memory = (row.get(f"{kind}_memories") or {}).get(depth, "")
                if not memory:
                    continue
                tot += 1
                keywords = TOPIC_KEYWORDS.get(row["proposition"]) or [row["proposition"]]
                if not any(k in memory for k in keywords):
                    om += 1
            if tot:
                result[f"{kind}_d{depth}"] = {"omitted": om, "total": tot}
    return result


def _format_identity(table: dict[str, dict]) -> str:
    lines = []
    for cond, value in table.items():
        lines.append(f"  {cond:<22} {value['identical']}/{value['total']} = "
                     f"{value['rate']:.3f}")
    return "\n".join(lines)


def main(paths: list[str]) -> None:
    print("=== memory identity between runs ===")
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            a, b = load_records(paths[i]), load_records(paths[j])
            table = memory_identity(a, b)
            rates = [v["rate"] for v in table.values()]
            mean = sum(rates) / len(rates) if rates else 0.0
            print(f"\n{paths[i]} vs {paths[j]}  (mean identity {mean:.3f})")
            print(_format_identity(table))

    print("\n=== per-run deterministic metrics ===")
    for path in paths:
        print(f"\n{path}")
        cue = summarize_records(Path(path) / "records.jsonl")
        for cond, value in cue.items():
            print(f"  cue {cond:<22} n={value['n']} MATCH={value['MATCH']} "
                  f"MIXED={value['MIXED']} OPPOSITE={value['OPPOSITE']} ABSENT={value['ABSENT']}")
        prop = condition_omission(path)
        for cond, value in prop.items():
            print(f"  prop_omit {cond:<22} {value['omitted']}/{value['total']}")


if __name__ == "__main__":
    main(sys.argv[1:])
