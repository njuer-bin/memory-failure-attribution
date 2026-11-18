"""Apply the three-item Stage 2 adjudication and report unadjudicated vs adjudicated agreement.

Usage:
    G:/aconda/python.exe -m experiments.apply_stage2_adjudication
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
from pathlib import Path

from experiments.analyze_stage2_calibration import compare, load

FIELDS = ["gold_dimension", "gold_status", "gold_strength"]
GATE_FIELDS = ["gold_dimension", "gold_status"]


def main() -> None:
    root = Path("results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", type=Path, default=root / "annotator_A.csv")
    parser.add_argument("--b", type=Path, default=root / "annotator_B.csv")
    parser.add_argument("--adjudication", type=Path,
                        default=root / "adjudication" / "adjudication_sheet.csv")
    parser.add_argument("--out", type=Path,
                        default=root / "analysis" / "agreement_adjudicated.json")
    args = parser.parse_args()

    rows_a, rows_b = load(args.a), load(args.b)
    with args.adjudication.open(encoding="utf-8-sig", newline="") as handle:
        adjudications = list(csv.DictReader(handle))
    if len(adjudications) != 3:
        raise SystemExit(f"expected 3 adjudications, got {len(adjudications)}")

    adj_a, adj_b = copy.deepcopy(rows_a), copy.deepcopy(rows_b)
    applied = []
    for row in adjudications:
        item_id = row["item_id"]
        values = {
            "gold_dimension": (row.get("adjudicated_dimension") or "").strip(),
            "gold_status": (row.get("adjudicated_status") or "").strip(),
            "gold_strength": (row.get("adjudicated_strength") or "").strip(),
        }
        if not all(values.values()):
            raise SystemExit(f"{item_id}: missing adjudicated value")
        for target in (adj_a, adj_b):
            record = next(r for r in target if r["item_id"] == item_id)
            for field, value in values.items():
                record[field] = value
        applied.append({"item_id": item_id, **values,
                        "rationale": (row.get("rationale") or "").strip()})

    report = {"n_items": len(rows_a), "adjudicated_items": applied,
              "unadjudicated": {}, "adjudicated": {}, "gates": {}}
    for field in FIELDS:
        before = compare(rows_a, rows_b, field)
        after = compare(adj_a, adj_b, field)
        report["unadjudicated"][field] = {
            "raw": before["raw_agreement"], "kappa": before["cohen_kappa"],
            "n_disagreements": len(before["disagreements"]),
        }
        report["adjudicated"][field] = {
            "raw": after["raw_agreement"], "kappa": after["cohen_kappa"],
            "n_disagreements": len(after["disagreements"]),
        }
    for field in GATE_FIELDS:
        item = report["adjudicated"][field]
        report["gates"][field] = {
            "raw": item["raw"], "kappa": item["kappa"],
            "pass": item["raw"] >= 0.85 and (item["kappa"] or 0) >= 0.70,
        }
    report["all_gates_pass"] = all(g["pass"] for g in report["gates"].values())

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    for field in FIELDS:
        u, a = report["unadjudicated"][field], report["adjudicated"][field]
        print(f"{field}: unadj raw={u['raw']:.3f} kappa={u['kappa']} | "
              f"adj raw={a['raw']:.3f} kappa={a['kappa']}")
    for field, gate in report["gates"].items():
        print(f"gate {field}: raw={gate['raw']:.3f} kappa={gate['kappa']} "
              f"{'PASS' if gate['pass'] else 'FAIL'}")
    print(f"ALL GATES: {'PASS' if report['all_gates_pass'] else 'FAIL'}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
