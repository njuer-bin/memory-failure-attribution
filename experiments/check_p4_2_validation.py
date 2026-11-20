"""Check the P4.2 two-human validation sheets against the protocol gates.

Usage:
    G:/aconda/python.exe -m experiments.check_p4_2_validation
    G:/aconda/python.exe -m experiments.check_p4_2_validation \
        --a results/status_drift_v3_p4_2/validation_A.csv \
        --b results/status_drift_v3_p4_2/validation_B.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

RATING_FIELDS = {
    "realism_1_5": 5,
    "status_clarity_1_5": 5,
    "rule_clarity_1_5": 5,
    "distortion_plausible_1_5": 5,
    "stake_severity_1_5": 5,
}
FLAG_FIELD = "only_status_differs"

GATES = {
    "realism_1_5": (4.0, "min"),
    "status_clarity_1_5": (4.0, "min"),
    "rule_clarity_1_5": (4.0, "min"),
    "distortion_plausible_1_5": (4.0, "min"),
    "stake_severity_1_5": (3.0, "min"),
}


def load(path: Path) -> dict[str, dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["scenario_id"].strip(): row for row in rows}


def norm(value: str) -> str:
    return (value or "").strip()


def numeric(row: dict, field: str) -> int | None:
    value = norm(row.get(field, ""))
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0 or n != len(b):
        return None
    labels = sorted(set(a) | set(b))
    observed = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = Counter(a), Counter(b)
    expected = sum((pa[label] / n) * (pb[label] / n) for label in labels)
    if expected == 1.0:
        return None
    return (observed - expected) / (1.0 - expected)


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def check_provenance(path: Path) -> dict:
    if not path.exists():
        return {"present": False}
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    required = ["annotator", "role", "date", "independent", "blind_to_expected",
                "read_validation_internal", "read_items_jsonl",
                "read_protocol_expected_section"]
    missing = [key for key in required if key not in data or data[key] in ("", None)]
    return {"present": True, "missing": missing, "data": data}


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path("results/status_drift_v3_p4_2")
    parser.add_argument("--a", type=Path, default=root / "validation_A.csv")
    parser.add_argument("--b", type=Path, default=root / "validation_B.csv")
    parser.add_argument("--out", type=Path,
                        default=root / "analysis" / "validation_summary.json")
    parser.add_argument("--provenance-prefix", default="validation_provenance")
    args = parser.parse_args()

    sheets = {"A": load(args.a), "B": load(args.b)}
    ids = sorted(set(sheets["A"]) | set(sheets["B"]))
    report: dict = {"sheets": {}, "items": {}, "scenarios": {}, "gates": {}}

    problems = []
    for name in ("A", "B"):
        missing = sorted(set(sheets["A"]) ^ set(sheets["B"]))
        if missing:
            problems.append(f"{name} scenario set differs: {missing}")
        invalid = []
        for sid, row in sheets[name].items():
            for field in RATING_FIELDS:
                value = numeric(row, field)
                if value is None or not 1 <= value <= 5:
                    invalid.append({"scenario_id": sid, "field": field,
                                    "value": norm(row.get(field, ""))})
            flag = norm(row.get(FLAG_FIELD, "")).lower()
            if flag not in ("yes", "no"):
                invalid.append({"scenario_id": sid, "field": FLAG_FIELD,
                                "value": norm(row.get(FLAG_FIELD, ""))})
            if not norm(row.get("notes", "")):
                invalid.append({"scenario_id": sid, "field": "notes",
                                "value": ""})
        report["sheets"][name] = {"rows": len(sheets[name]),
                                  "invalid": invalid}

    # Per-field means, agreement, and dispersion.
    for field in RATING_FIELDS:
        per = {}
        pooled = []
        for name in ("A", "B"):
            values = [numeric(sheets[name][sid], field) for sid in ids]
            values = [value for value in values if value is not None]
            per[name] = {"mean": mean(values), "n": len(values)}
            pooled.extend(values)
        report["items"][field] = {
            "pooled_mean": mean(pooled),
            "per_annotator": per,
            "exact_agreement": mean([
                1.0 if numeric(sheets["A"][sid], field) == numeric(sheets["B"][sid], field) else 0.0
                for sid in ids
            ]),
            "mean_abs_difference": mean([
                abs(numeric(sheets["A"][sid], field) - numeric(sheets["B"][sid], field))
                for sid in ids
                if numeric(sheets["A"][sid], field) is not None
                and numeric(sheets["B"][sid], field) is not None
            ]),
        }

    flags_a = [norm(sheets["A"][sid][FLAG_FIELD]).lower() for sid in ids]
    flags_b = [norm(sheets["B"][sid][FLAG_FIELD]).lower() for sid in ids]
    report["items"][FLAG_FIELD] = {
        "yes_pooled": sum(1 for value in flags_a + flags_b if value == "yes")
                     / (len(flags_a) + len(flags_b)),
        "yes_both": sum(1 for a, b in zip(flags_a, flags_b) if a == b == "yes") / len(ids),
        "yes_either": sum(1 for a, b in zip(flags_a, flags_b) if a == "yes" or b == "yes") / len(ids),
        "exact_agreement": sum(1 for a, b in zip(flags_a, flags_b) if a == b) / len(ids),
        "cohen_kappa": cohen_kappa(flags_a, flags_b),
        "disagreements": [
            {"scenario_id": sid, "A": a, "B": b}
            for sid, a, b in zip(ids, flags_a, flags_b) if a != b
        ],
    }

    # Exclusion candidates and survivors.
    excluded = []
    for sid in ids:
        reasons = []
        for name in ("A", "B"):
            row = sheets[name][sid]
            if norm(row[FLAG_FIELD]).lower() != "yes":
                reasons.append(f"only_status_differs={norm(row[FLAG_FIELD])} ({name})")
            if (numeric(row, "status_clarity_1_5") or 5) <= 2:
                reasons.append(f"status_clarity={numeric(row, 'status_clarity_1_5')} ({name})")
            if (numeric(row, "rule_clarity_1_5") or 5) <= 2:
                reasons.append(f"rule_clarity={numeric(row, 'rule_clarity_1_5')} ({name})")
        if reasons:
            excluded.append({"scenario_id": sid, "reasons": reasons,
                             "A_notes": norm(sheets["A"][sid].get("notes", "")),
                             "B_notes": norm(sheets["B"][sid].get("notes", ""))})
    report["scenarios"] = {
        "total": len(ids),
        "excluded": excluded,
        "survivors": len(ids) - len(excluded),
    }

    gate_results = {}
    for field, (threshold, _) in GATES.items():
        value = report["items"][field]["pooled_mean"]
        gate_results[field] = {"threshold": threshold, "value": value,
                               "pass": value is not None and value >= threshold}
    gate_results["only_status_differs"] = {
        "threshold": 0.95,
        "value": report["items"][FLAG_FIELD]["yes_both"],
        "pass": report["items"][FLAG_FIELD]["yes_both"] >= 0.95,
    }
    gate_results["survivors"] = {
        "threshold": 36,
        "value": report["scenarios"]["survivors"],
        "pass": report["scenarios"]["survivors"] >= 36,
    }
    per_annotator = {}
    for field, (threshold, _) in GATES.items():
        per_annotator[field] = {
            name: {"value": report["items"][field]["per_annotator"][name]["mean"],
                   "pass": (report["items"][field]["per_annotator"][name]["mean"] or 0) >= threshold}
            for name in ("A", "B")
        }
    report["gates"] = {
        "interpretation": "scenario means; ratings pooled across both annotators",
        "checks": gate_results,
        "per_annotator_checks": per_annotator,
        "all_pass": all(check["pass"] for check in gate_results.values()),
    }

    provenance = {name: check_provenance(args.a.parent / f"{args.provenance_prefix}_{name}.json")
                  for name in ("A", "B")}
    report["provenance"] = provenance
    report["warnings"] = problems
    if not all(item["present"] and not item.get("missing") for item in provenance.values()):
        report["warnings"].append(
            "provenance incomplete: validation_provenance_A.json / _B.json missing or unfilled; "
            "the gate is provisional until provenance is recorded")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print(f"scenarios: {len(ids)}  survivors: {report['scenarios']['survivors']}")
    for field in list(RATING_FIELDS) + [FLAG_FIELD]:
        item = report["items"][field]
        if field == FLAG_FIELD:
            print(f"{field}: yes_both={fmt(item['yes_both'])} "
                  f"agreement={fmt(item['exact_agreement'])} kappa={fmt(item['cohen_kappa'])}")
        else:
            print(f"{field}: pooled_mean={fmt(item['pooled_mean'])} "
                  f"A={fmt(item['per_annotator']['A']['mean'])} "
                  f"B={fmt(item['per_annotator']['B']['mean'])} "
                  f"agreement={fmt(item['exact_agreement'])}")
    for name, check in gate_results.items():
        print(f"gate {name}: value={check['value']} threshold={check['threshold']} "
              f"{'PASS' if check['pass'] else 'FAIL'}")
    print(f"ALL GATES: {'PASS' if report['gates']['all_pass'] else 'FAIL'}")
    if excluded:
        print("excluded:")
        for item in excluded:
            print(f"  {item['scenario_id']}: {'; '.join(item['reasons'])}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
