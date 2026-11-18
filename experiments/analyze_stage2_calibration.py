"""Analyze the Stage 2 60-item gold calibration.

Usage:
    G:/aconda/python.exe -m experiments.analyze_stage2_calibration
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from experiments.check_annotations import cohen_kappa

CATEGORICAL = [
    "gold_dimension", "gold_status", "gold_condition_state",
    "gold_action_state", "gold_strength", "gold_confidence",
]
CONDITIONAL_FIELDS = ["gold_condition_state", "gold_action_state"]
TEXT_FIELDS = ["target_proposition", "evidence_quote"]


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (value or "").lower()).strip()


def tokens(value: str) -> set[str]:
    return set(norm(value).split())


def jaccard(a: str, b: str) -> float | None:
    left, right = tokens(a), tokens(b)
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def compare(rows_a: list[dict], rows_b: list[dict], field: str,
            subset: list[dict] | None = None) -> dict:
    source = subset if subset is not None else rows_a
    pairs = []
    for row_a in source:
        row_b = next(r for r in rows_b if r["item_id"] == row_a["item_id"])
        pairs.append(((row_a.get(field) or "").strip(),
                      (row_b.get(field) or "").strip()))
    if not pairs:
        return {"n": 0}
    a = [x for x, _ in pairs]
    b = [y for _, y in pairs]
    result = {
        "n": len(pairs),
        "raw_agreement": sum(x == y for x, y in pairs) / len(pairs),
        "cohen_kappa": cohen_kappa(a, b),
        "A_distribution": dict(Counter(a)),
        "B_distribution": dict(Counter(b)),
        "disagreements": [
            {"item_id": row["item_id"], "A": x, "B": y}
            for row, (x, y) in zip(source, pairs) if x != y
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path("results/status_drift_v3_real_audit/stage2_calibration_60")
    parser.add_argument("--a", type=Path, default=root / "annotator_A.csv")
    parser.add_argument("--b", type=Path, default=root / "annotator_B.csv")
    parser.add_argument("--out", type=Path, default=root / "analysis" / "agreement.json")
    args = parser.parse_args()

    rows_a, rows_b = load(args.a), load(args.b)
    if len(rows_a) != len(rows_b) or not rows_a:
        raise SystemExit(f"A/B row mismatch: A={len(rows_a)} B={len(rows_b)}")

    conditional = [row for row in rows_a
                   if (row.get("gold_dimension") or "").strip().lower() == "conditional"]
    report: dict = {
        "n_items": len(rows_a),
        "n_conditional": len(conditional),
        "fields": {},
        "gates": {},
    }
    for field in CATEGORICAL:
        subset = conditional if field in CONDITIONAL_FIELDS else None
        report["fields"][field] = compare(rows_a, rows_b, field, subset)
    for field in TEXT_FIELDS:
        pairs = [(norm(row[field]), norm(next(r for r in rows_b
                                              if r["item_id"] == row["item_id"])[field]))
                 for row in rows_a]
        report["fields"][field] = {
            "n": len(pairs),
            "normalized_exact_agreement": sum(x == y for x, y in pairs) / len(pairs),
            "mean_token_jaccard": sum(jaccard(x, y) or 0 for x, y in pairs) / len(pairs),
        }

    dimension = report["fields"]["gold_dimension"]
    status = report["fields"]["gold_status"]
    report["gates"] = {
        "gold_dimension": {
            "raw": dimension["raw_agreement"], "kappa": dimension["cohen_kappa"],
            "pass": dimension["raw_agreement"] >= 0.85
                    and (dimension["cohen_kappa"] or 0) >= 0.70,
        },
        "gold_status": {
            "raw": status["raw_agreement"], "kappa": status["cohen_kappa"],
            "pass": status["raw_agreement"] >= 0.85
                    and (status["cohen_kappa"] or 0) >= 0.70,
        },
    }
    if conditional:
        for field in CONDITIONAL_FIELDS:
            item = report["fields"][field]
            report["gates"][field] = {
                "raw": item["raw_agreement"], "kappa": item["cohen_kappa"],
                "pass": item["raw_agreement"] >= 0.85
                        and (item["cohen_kappa"] or 0) >= 0.70,
            }
    report["all_gates_pass"] = all(gate["pass"] for gate in report["gates"].values())

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(f"items: {report['n_items']}  conditional: {report['n_conditional']}")
    for field in CATEGORICAL:
        item = report["fields"][field]
        if "raw_agreement" not in item:
            print(f"{field}: n=0 (not applicable)")
            continue
        print(f"{field}: raw={item['raw_agreement']:.3f} "
              f"kappa={item['cohen_kappa']} n={item['n']}")
    for field in TEXT_FIELDS:
        item = report["fields"][field]
        print(f"{field}: exact={item['normalized_exact_agreement']:.3f} "
              f"jaccard={item['mean_token_jaccard']:.3f}")
    for field, gate in report["gates"].items():
        print(f"gate {field}: raw={gate['raw']:.3f} kappa={gate['kappa']} "
              f"{'PASS' if gate['pass'] else 'FAIL'}")
    print(f"ALL GATES: {'PASS' if report['all_gates_pass'] else 'FAIL'}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
